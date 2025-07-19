# Enhanced Car Recommendation System with ChromaDB

This enhanced recommendation system uses ChromaDB to query car information and provide intelligent recommendations based on user needs.

## How it Works

1. **Data Storage**: Car data from `cars_data.json` is already stored in ChromaDB via the UI
2. **Query Processing**: The recommendation agent queries ChromaDB using semantic search
3. **LLM Analysis**: The retrieved car data is analyzed by Azure OpenAI to structure recommendations
4. **Intelligent Matching**: Cars are ranked based on user criteria and preferences

## Key Features

- **Semantic Search**: Uses vector similarity to find relevant cars
- **Natural Language Processing**: Extracts user criteria from conversational input
- **Intelligent Ranking**: Scores cars based on multiple factors
- **Comprehensive Analysis**: Provides detailed explanations for recommendations

## Components

### 1. Enhanced Recommendation Agent (`agents/recommendation/recommendation_agent.py`)

- **`query_cars_from_chromadb()`**: Queries ChromaDB for relevant car information
- **`analyze_car_data_with_llm()`**: Uses LLM to structure and analyze retrieved data
- **`extract_user_criteria()`**: Extracts user preferences from natural language
- **`rank_recommendations()`**: Ranks cars based on match scores

### 2. Demo Script (`demo_recommendations.py`)

- Interactive demo to test the recommendation system
- Sample queries to demonstrate different scenarios
- Works with existing ChromaDB data

## Usage

### Prerequisites

1. Make sure car data is loaded in ChromaDB via the UI:
   - Use the Knowledge Base Management tab
   - Upload `cars_data.json` file
   - Process and embed the documents

### Running the Demo

```bash
python3 demo_recommendations.py
```

Choose from:
1. **Automated Demo**: See sample recommendations with predefined queries
2. **Interactive Demo**: Enter your own car preferences and get recommendations
3. **Database Stats**: View ChromaDB statistics

### Integration with Main Chat System

The enhanced recommendation agent is automatically used when the orchestration agent routes car recommendation requests to the `recommend_car` function.

## Example Queries

- "I need a family car under $30,000 with good safety ratings"
- "Looking for a luxury car for business meetings with latest technology"
- "Need an eco-friendly car for daily commuting"
- "Want a sporty car for weekend drives and performance"
- "Need a budget-friendly first car that's reliable"

## Technical Details

### ChromaDB Integration

The system uses the existing ChromaDB instance configured in `services.py` and initialized in `knowledge_base.py`. No additional data ingestion is needed since the car data is already loaded via the UI.

### Search Strategy

1. **Query Building**: Constructs search queries based on user criteria (budget, purposes, priorities)
2. **Semantic Search**: Uses ChromaDB's similarity search to find relevant car information
3. **LLM Processing**: Analyzes retrieved data to extract structured car information
4. **Ranking**: Scores and ranks cars based on match criteria

### Response Generation

The system provides:
- **Detailed Analysis**: Explanation of user needs
- **Top 3 Recommendations**: Best matching cars with scores
- **Why Recommended**: Specific reasons for each recommendation
- **Key Features**: Important specifications and advantages

## Maintenance

- **Data Updates**: Simply re-upload updated car data via the UI
- **Query Tuning**: Adjust search parameters in `query_cars_from_chromadb()`
- **Response Customization**: Modify prompts in `analyze_car_data_with_llm()` and `generate_recommendation_response()`
