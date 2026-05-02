"""
(Module 2) RAG Triad execution & Tracing
"""
import os
import sys

# Ensure we can import from eval_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Step 6 requirement: Ensure LANGCHAIN_TRACING_V2 is enabled
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "llm-eval-suite"

from eval_engine.eval_config import local_llm, local_embeddings, eval_tracer
from eval_engine.mock_datasets import QUESTIONS, GROUND_TRUTH_ANSWERS, SAMPLE_CONTEXTS
from langchain_core.runnables import RunnableConfig

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import faithfulness, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig

if __name__ == "__main__":
    print("Setting up RAG Triad Evaluation...")

    # Step 4: Loading metrics and binding local models (Wrapped for Ragas 0.2.6)
    ragas_llm = LangchainLLMWrapper(local_llm)
    ragas_embeddings = LangchainEmbeddingsWrapper(local_embeddings)
    
    faithfulness.llm = ragas_llm
    context_precision.llm = ragas_llm
    context_recall.llm = ragas_llm
    
    context_precision.embeddings = ragas_embeddings
    context_recall.embeddings = ragas_embeddings

    # Step 5: Create samples using data from mock_datasets.py
    # Pick one HTML (idx 0), one JS (idx 5), and one SQL (idx 7)
    
    sample1 = SingleTurnSample(
        user_input=QUESTIONS[0],
        response=f"The answer is: {GROUND_TRUTH_ANSWERS[0]}",
        retrieved_contexts=[GROUND_TRUTH_ANSWERS[0], SAMPLE_CONTEXTS[0]],
        reference=GROUND_TRUTH_ANSWERS[0]
    )

    sample2 = SingleTurnSample(
        user_input=QUESTIONS[5],
        response=f"The answer is: {GROUND_TRUTH_ANSWERS[5]}",
        retrieved_contexts=[GROUND_TRUTH_ANSWERS[5], SAMPLE_CONTEXTS[1]],
        reference=GROUND_TRUTH_ANSWERS[5]
    )

    sample3 = SingleTurnSample(
        user_input=QUESTIONS[7],
        response=f"The answer is: {GROUND_TRUTH_ANSWERS[7]}",
        retrieved_contexts=[GROUND_TRUTH_ANSWERS[7], SAMPLE_CONTEXTS[2]],
        reference=GROUND_TRUTH_ANSWERS[7]
    )

    # Creating EvaluationDataset
    eval_dataset = EvaluationDataset(samples=[sample1, sample2, sample3])



    print("Running EvaluationDataset with local LLM and Embeddings...")
    
    # Executing the RAG triad metrics
    # Added RunConfig with high timeout and max_workers=1 so Ollama isn't overwhelmed
    run_config = RunConfig(timeout=300, max_workers=1)
    
    result = evaluate(
        dataset=eval_dataset,
        metrics=[faithfulness, context_precision, context_recall],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        run_config=run_config
    )

    # Convert to pandas dataframe
    df = result.to_pandas()
    print("\nEvaluation Results:")
    print(df[['user_input', 'faithfulness', 'context_precision', 'context_recall']])

    # Step 6: Practical Deployment Gate
    # Check if any faithfulness score < 0.6
    min_faithfulness = df['faithfulness'].min()
    print(f"\nMinimum Faithfulness Score: {min_faithfulness}")
    
    if min_faithfulness < 0.6:
        print("❌ Practical Deployment Gate Failed: Faithfulness score is below 0.6. Aborting deployment.")
        sys.exit(1)
    else:
        print("✅ Practical Deployment Gate Passed: All faithfulness scores are >= 0.6.")
