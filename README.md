# LLM Evaluation Framework

This project is a Python-based framework designed to evaluate and compare the performance of different Large Language Models (LLMs) using the OpenRouter API. It runs a series of standardized experiments to assess capabilities such as instruction following, formatting adherence, consistency, and style control.

## Project Structure

- **`assignment.py`**: The main script that orchestrates the experiments, communicates with the OpenRouter API, and evaluates the model responses.
- **`log.py`**: A utility module handling the initialization and writing of experiment results to a CSV file.
- **`results.csv`**: The output file where all experiment metrics and results are logged.
- **`Genral Comparison Report.pdf`**: A report comparing the general performance of the models.

## Features & Experiments

The framework runs the following 6 experiments on selected models (currently configured for `moonshotai/kimi-k2:free` and `openai/gpt-oss-20b:free`):

1.  **Temperature Sweep**: Analyzes how different temperature settings (0.0, 0.7, 1.3) affect the word count of the output.
2.  **Strict JSON Format**: Tests the model's ability to generate valid JSON output with a specific schema (title, pros, cons) and no extra keys.
3.  **Quote-only QA**: Evaluates whether the model can answer questions based *strictly* on a provided passage and handle unanswerable queries correctly.
4.  **Translation & Back-translation**: Checks the preservation of meaning and proper nouns (e.g., "Albert Einstein") after translating text to Hindi and back to English.
5.  **Seed Stability**: Verifies if using a fixed seed produces deterministic (identical) outputs across multiple runs.
6.  **Style Control**: Tests the model's adherence to specific persona instructions (e.g., speaking like Yoda) and length constraints.

## Setup & Installation

1.  **Prerequisites**: Ensure you have Python installed.
2.  **Install Dependencies**: Install the required Python packages (primarily `openai` client).

    ```bash
    pip install openai
    ```

3.  **API Configuration**:
    -   Open `assignment.py`.
    -   Enter your OpenRouter API key in the `api_key` field within the `OpenAI` client setup (Line 10).

    ```python
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="your_openrouter_api_key_here"
    )
    ```

## Usage

Run the main assignment script to execute all experiments:

```bash
python assignment.py
```

Upon completion, the script will print a summary message, and the detailed metrics for each run will be saved in `results.csv`.

## Output Format (`results.csv`)

The CSV log includes the following fields for each run:
-   `timestamp`: Date and time of the run.
-   `model_id`: The identifier of the model used.
-   `task`: The name of the experiment (e.g., `temp_sweep`, `strict_json`).
-   `temperature`: Temperature setting used.
-   `seed`: Random seed used (if any).
-   `prompt_chars`, `completion_chars`: Token/character usage stats.
-   `latency_ms`: Time taken for the response.
-   `passed`: Boolean indicating if the test criteria were met.
-   `notes`: Additional observations or error messages.
