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

from eval_engine.eval_config import local_llm, local_embeddings, eval_tracer
from eval_engine.mock_datasets import QUESTIONS, GROUND_TRUTH_ANSWERS, SAMPLE_CONTEXTS
from langchain_core.runnables import RunnableConfig

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import faithfulness, context_precision, context_recall

if __name__ == "__main__":
    print("Setting up RAG Triad Evaluation...")

    # Step 4: Loading metrics and binding local models
    faithfulness.llm = local_llm
    context_precision.llm = local_llm
    context_recall.llm = local_llm
    
    
    context_precision.embeddings = local_embeddings
    context_recall.embeddings = local_embeddings

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
    result = evaluate(
        dataset=eval_dataset,
        metrics=[faithfulness, context_precision, context_recall],
        llm=local_llm,
        embeddings=local_embeddings,
        run_config=RunnableConfig(callbacks=[eval_tracer])
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
