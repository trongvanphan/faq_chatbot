# ChromaDB Car Recommendation System

This system has been enhanced to use ChromaDB for retrieving car information instead of hardcoded data. The recommendation agent now queries the car database from ChromaDB for more dynamic and comprehensive recommendations.

## Setup Instructions

### 1. Install Dependencies
Make sure all required packages are installed:
```bash
pip install -r requirements.txt
```

### 2. Ingest Car Data into ChromaDB
Before using the recommendation system, you need to ingest the car data from `data/cars_data.json` into ChromaDB:

```bash
python ingest_cars.py
```

This script will:
- Check if ChromaDB is properly configured
- Load car data from `data/cars_data.json`
- Process and format each car record for optimal semantic search
- Store the data in ChromaDB with rich metadata
- Provide statistics on the ingestion process

### 3. Environment Configuration
Ensure your `.env` file contains the necessary Azure OpenAI configuration:

```env
AZURE_OPENAI_EMBEDDING_ENDPOINT=your_embedding_endpoint
AZURE_OPENAI_EMBEDDING_API_KEY=your_embedding_api_key
AZURE_OPENAI_EMBEDDING_MODEL=your_embedding_model

AZURE_OPENAI_LLM_ENDPOINT=your_llm_endpoint
AZURE_OPENAI_LLM_API_KEY=your_llm_api_key
AZURE_OPENAI_LLM_MODEL=your_llm_model

CHROMA_DB_PATH=.chromadb
```

## How It Works

### 1. User Query Processing
When a user asks for car recommendations, the system:
- Extracts user criteria (budget, purposes, priorities, etc.)
- Converts criteria into semantic search queries
- Queries ChromaDB for relevant car information

### 2. Semantic Car Search
The system performs sophisticated semantic search by:
- Building comprehensive text descriptions for each car
- Including purpose-specific keywords and descriptions
- Mapping user priorities to car features
- Using ChromaDB's similarity search with Azure OpenAI embeddings

### 3. LLM-Powered Analysis
Retrieved car data is processed by the LLM to:
- Extract structured information about matching cars
- Score each car based on user criteria
- Generate explanations for why each car matches user needs

### 4. Intelligent Recommendations
The final recommendations include:
- Top 3 most suitable cars
- Match scores and explanations
- Detailed car specifications
- Personalized advice based on user needs

## Key Features

### Enhanced Semantic Search
- Rich text descriptions for each car including purposes, priorities, and features
- Semantic mapping of user needs to car capabilities
- Context-aware search that understands car buying terminology

### Dynamic Data Retrieval
- No hardcoded car database - all data retrieved from ChromaDB
- Easy to update with new car data
- Scalable to large datasets

### Intelligent Matching
- LLM-powered analysis of car data vs. user criteria
- Sophisticated scoring system
- Contextual recommendations with explanations

## File Structure

```
├── agents/recommendation/
│   ├── recommendation_agent.py    # Enhanced ChromaDB-based recommendation agent
│   └── car_database.py           # Validation constants (purposes, priorities, etc.)
├── car_data_ingestion.py         # Utility for ingesting car data into ChromaDB
├── ingest_cars.py                # Simple script to load car data
├── data/
│   └── cars_data.json            # Original car data (unchanged)
└── .chromadb/                    # ChromaDB storage directory
```

## Usage Examples

### Manual Car Data Ingestion
```python
from car_data_ingestion import CarDataIngestor

ingestor = CarDataIngestor()
results = ingestor.ingest_car_data("data/cars_data.json")
print(f"Processed {results['processed_cars']} cars")
```

### Check Database Statistics
```python
from car_data_ingestion import CarDataIngestor

ingestor = CarDataIngestor()
stats = ingestor.get_car_data_stats()
print(f"Total car records: {stats['total_car_records']}")
```

### Clear Car Data
```python
from car_data_ingestion import CarDataIngestor

ingestor = CarDataIngestor()
ingestor.clear_car_data()
```

## Recommendation Agent Features

### Criteria Extraction
- Automatic extraction of user preferences from natural language
- Support for budget, purposes, priorities, brand preferences, etc.
- Fallback to keyword extraction if LLM extraction fails

### ChromaDB Integration
- Semantic search across car database
- Rich metadata storage and retrieval
- Efficient similarity scoring

### Response Generation
- Comprehensive recommendations with detailed explanations
- Match scores and reasoning
- Formatted for easy reading

## Troubleshooting

### ChromaDB Issues
- Ensure proper permissions for `.chromadb` directory
- Check Azure OpenAI embedding configuration
- Verify network connectivity for API calls

### Data Ingestion Problems
- Verify `data/cars_data.json` exists and is valid JSON
- Check file permissions
- Monitor logs for specific error messages

### Recommendation Quality
- Ensure car data has been properly ingested
- Check that embedding model is working correctly
- Verify LLM model configuration

## Benefits of ChromaDB Integration

1. **Scalability**: Can handle large car datasets efficiently
2. **Flexibility**: Easy to update car data without code changes
3. **Intelligence**: Semantic search provides better matching than keyword-based filtering
4. **Maintainability**: Separation of data storage and business logic
5. **Performance**: Vector search is optimized for similarity queries

The system now provides more intelligent, context-aware car recommendations by leveraging the power of ChromaDB and LLM analysis.
