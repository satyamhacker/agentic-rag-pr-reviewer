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

    # Step 5: 3 sample entries for the dataset mapped to pdfs
    sample1 = SingleTurnSample(
        user_input="What is the semantic HTML tag for navigation?",
        response="The <nav> tag is used for navigation links.",
        retrieved_contexts=["HTML5 introduced the <nav> semantic tag. It represents a section of a page whose purpose is to provide navigation links."],
        reference="The <nav> tag is used to define navigation menus."
    )

    sample2 = SingleTurnSample(
        user_input="How do you declare a block-scoped variable in JavaScript?",
        response="You can use let or const to declare a block-scoped variable.",
        retrieved_contexts=["In ES6, JavaScript introduced let and const for block-scoped variable declarations, unlike var which is function-scoped."],
        reference="Use let or const for block-scoped variables."
    )

    sample3 = SingleTurnSample(
        user_input="What is the correct SQL syntax for an INNER JOIN?",
        response="SELECT columns FROM table1 INNER JOIN table2 ON table1.column = table2.column;",
        retrieved_contexts=["An INNER JOIN selects records that have matching values in both tables. Syntax: SELECT * FROM t1 INNER JOIN t2 ON t1.id = t2.id;"],
        reference="SELECT column_name(s) FROM table1 INNER JOIN table2 ON table1.column_name = table2.column_name;"
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
