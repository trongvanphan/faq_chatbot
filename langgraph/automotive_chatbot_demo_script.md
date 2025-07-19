# 🚗 Automotive Chatbot Demo Script
*Comprehensive demonstration of all use cases and features*

---

## 📋 Pre-Demo Setup Checklist

### Environment Setup
- [ ] **Environment Variables**: Verify all Azure OpenAI credentials are configured
  ```bash
  AZURE_OPENAI_LLM_ENDPOINT=your_llm_endpoint
  AZURE_OPENAI_LLM_API_KEY=your_llm_api_key
  AZURE_OPENAI_LLM_MODEL=your_model_name
  AZURE_OPENAI_EMBEDDING_ENDPOINT=your_embedding_endpoint
  AZURE_OPENAI_EMBEDDING_API_KEY=your_embedding_api_key
  AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
  ```

- [ ] **Dependencies**: Install all required packages
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Application Launch**: Start the Streamlit application
  ```bash
  streamlit run app.py
  ```

- [ ] **Knowledge Base**: Upload `cars_data.json` via the Knowledge Base tab (if not already done)

---

## 🎬 Demo Structure

### Demo Flow Overview:
1. **Application Introduction** (2 minutes)
2. **Knowledge Base Management** (3 minutes)
3. **Chat Interface - Car Recommendations** (5 minutes)
4. **Chat Interface - Document Search** (3 minutes)
5. **Chat Interface - News Search** (2 minutes)
6. **Advanced Features & Architecture** (3 minutes)
7. **Extension Points** (2 minutes)

**Total Demo Time: ~20 minutes**

---

## 🌟 Demo Script

### **1. Application Introduction (2 minutes)**

**Script:**
> "Welcome to the Automotive Chatbot - a sophisticated multi-agent AI system designed specifically for automotive assistance. This application demonstrates advanced RAG (Retrieval-Augmented Generation) capabilities combined with intelligent agent orchestration using LangGraph."

**Show:**
- Navigate to the application homepage
- Point out the dual-tab interface (Chat / Knowledge Base)

**Key Points:**
- Multi-agent architecture with intelligent routing
- Enhanced document processing with MarkItDown
- ChromaDB vector database for semantic search
- Azure OpenAI integration for LLM and embeddings

---

### **2. Knowledge Base Management (3 minutes)**

**Navigate to:** Knowledge Base tab

#### **2.1 Document Upload Demonstration**

**Script:**
> "Let's start by exploring our knowledge base management system. This is where we can upload and process documents to build our AI's knowledge."

**Demo Actions:**
1. Show the file upload interface
2. Demonstrate supported file types (PDF, TXT, DOCX, JSON)
3. Explain chunk size and overlap configuration
4. If `cars_data.json` isn't uploaded, upload it now

**Sample Prompts/Actions:**
- Upload a sample PDF or text file
- Adjust chunk size to 300 words, overlap to 25
- Click "Process and Embed Documents"
- Show the processing progress and results

#### **2.2 Database Statistics & Search**

**Script:**
> "Once documents are processed, we can see comprehensive statistics and search our knowledge base directly."

**Demo Actions:**
1. Show database statistics (total chunks, unique sources)
2. Demonstrate knowledge base search functionality
3. Show the LangGraph workflow diagram

**Sample Search Queries:**
```
"Honda Civic specifications"
"luxury car features"
"fuel economy comparison"
"safety ratings"
```

**Show Results:**
- Similarity scores
- Source metadata
- Content previews

#### **2.3 Agent Status Sidebar**

**Script:**
> "In the sidebar, you can see all available agents and their capabilities, plus visualize our LangGraph workflow."

**Demo Actions:**
- Show available agents list
- Click "Show LangGraph Workflow" 
- Explain the workflow diagram (router → agents → answer generation)

---

### **3. Chat Interface - Car Recommendations (5 minutes)**

**Navigate to:** Chat tab

**Script:**
> "Now let's explore our intelligent chat interface. The system automatically routes queries to the most appropriate agent based on intent classification."

#### **3.1 Basic Car Recommendation**

**Sample Prompt 1:**
```
"I need a car recommendation for my family of 4 with a budget of $35,000"
```

**Expected Response:** 
- Agent should route to recommendation agent
- Provide 3 ranked car suggestions
- Include detailed explanations with price, features, and match reasoning

**Demo Points:**
- Point out the intent classification in action
- Show comprehensive recommendations with match scores
- Explain the multi-criteria scoring system

#### **3.2 Specific Use Case Recommendations**

**Sample Prompt 2:**
```
"What car should I buy for daily commuting that's fuel efficient?"
```

**Sample Prompt 3:**
```
"Recommend a luxury car for business meetings with latest technology"
```

**Sample Prompt 4:**
```
"I need a reliable car for weekend outdoor adventures"
```

**Demo Points:**
- Show how different criteria affect recommendations
- Point out purpose-based matching
- Highlight technology and feature recommendations

#### **3.3 Budget-Specific Recommendations**

**Sample Prompt 5:**
```
"Show me the best cars under $25,000 for a first-time buyer"
```

**Sample Prompt 6:**
```
"I want a premium car with a budget up to $60,000"
```

**Demo Points:**
- Demonstrate budget-based filtering
- Show price-appropriate recommendations
- Explain value proposition reasoning

---

### **4. Chat Interface - Document Search (3 minutes)**

**Script:**
> "The system also excels at document retrieval and knowledge base queries, using semantic search to find relevant information."

#### **4.1 General Information Queries**

**Sample Prompt 1:**
```
"Tell me about car maintenance schedules"
```

**Sample Prompt 2:**
```
"What information do you have about warranty coverage?"
```

**Sample Prompt 3:**
```
"Search for car safety features information"
```

**Demo Points:**
- Show semantic search in action
- Point out source attribution
- Demonstrate context-aware responses

#### **4.2 Specific Car Model Queries**

**Sample Prompt 4:**
```
"Find information about Honda Civic features"
```

**Sample Prompt 5:**
```
"What are the specifications of Toyota Camry?"
```

**Demo Points:**
- Show model-specific information retrieval
- Highlight comprehensive data extraction
- Explain how ChromaDB enables semantic matching

---

### **5. Chat Interface - News Search (2 minutes)**

**Script:**
> "Our system can also search for current automotive news and updates using external APIs."

#### **5.1 General Automotive News**

**Sample Prompt 1:**
```
"Show me latest automotive industry news"
```

**Sample Prompt 2:**
```
"What's new in electric vehicles?"
```

#### **5.2 Technology and Trends**

**Sample Prompt 3:**
```
"Recent updates in autonomous driving technology"
```

**Sample Prompt 4:**
```
"Latest car safety technology innovations"
```

**Demo Points:**
- Show external API integration
- Demonstrate real-time information access
- Point out current vs. historical information distinction

---

### **6. Advanced Features & Architecture (3 minutes)**

**Script:**
> "Let's explore the technical architecture that makes this intelligent routing possible."

#### **6.1 Multi-Agent Architecture**

**Key Points to Highlight:**
- **Master Orchestration Agent**: Central coordinator with LangGraph workflows
- **Intent Classification**: LLM-powered routing decisions
- **Specialized Agents**: Car recommendations, document retrieval, news search
- **State Management**: Consistent ChatState across all agents

#### **6.2 Technology Stack**

**Demonstrate:**
- **ChromaDB Integration**: Vector similarity search
- **Azure OpenAI**: GPT models and embeddings
- **LangChain/LangGraph**: Workflow orchestration
- **MarkItDown**: Enhanced document parsing
- **Streamlit**: Interactive web interface

#### **6.3 Error Handling & Fallbacks**

**Sample Prompt:**
```
"This is a completely unrelated query about quantum physics"
```

**Demo Points:**
- Show graceful handling of off-topic queries
- Demonstrate fallback mechanisms
- Point out error recovery in the workflow

---

### **7. Extension Points (2 minutes)**

**Script:**
> "The system is designed for easy extension with new agents and capabilities."

#### **7.1 Agent Registration System**

**Show Code Example:**
```python
from orchestration_agent import master_agent

def custom_agent(state: ChatState) -> ChatState:
    return {**state, "answer": "Custom response"}

master_agent.add_agent(
    name="custom_agent",
    function=custom_agent,
    description="Handles custom queries",
    keywords=["custom", "special", "unique"]
)
```

#### **7.2 Supported Extension Types**

**Highlight:**
- **New Document Types**: Additional parsers can be added
- **External APIs**: Integration with more automotive data sources
- **Custom Workflows**: New LangGraph workflows for complex processes
- **UI Enhancements**: Additional Streamlit components

---

## 🎯 Demo Tips & Best Practices

### **Before Starting:**
- Clear chat history for a clean demo
- Ensure stable internet connection for news searches
- Have backup prompts ready if APIs are slow
- Test all sample prompts beforehand

### **During Demo:**
- **Pace**: Allow time for responses to generate
- **Explain**: Describe what's happening during loading
- **Interact**: Encourage audience questions
- **Highlight**: Point out unique features and technical capabilities

### **Common Questions & Answers:**

**Q: "How does the system know which agent to use?"**
A: "The master orchestration agent uses Azure OpenAI to classify user intent based on keywords and context, then routes to the most appropriate specialized agent using LangGraph workflows."

**Q: "Can you add new car data?"**
A: "Absolutely! You can upload new JSON files through the Knowledge Base tab. The system will process and embed the new data automatically."

**Q: "How accurate are the recommendations?"**
A: "The recommendations are based on a multi-criteria scoring system that considers budget, purpose, priorities, and brand preferences. The system currently has data for 50+ car models with comprehensive specifications."

**Q: "Can this work with other domains besides automotive?"**
A: "Yes! The multi-agent architecture is domain-agnostic. You can easily swap out the car recommendation agent for agents specific to other industries."

---

## 📊 Success Metrics for Demo

### **Engagement Indicators:**
- [ ] Audience asks technical questions about architecture
- [ ] Interest in extending the system for other use cases
- [ ] Positive feedback on response quality and speed
- [ ] Questions about deployment and scaling

### **Technical Demonstration Success:**
- [ ] All agents respond correctly to their intended queries
- [ ] Document search returns relevant results with good similarity scores
- [ ] News search provides current information
- [ ] Workflow diagram displays correctly
- [ ] No errors or timeouts during demo

### **Business Value Demonstration:**
- [ ] Clear understanding of multi-agent benefits
- [ ] Recognition of RAG improvement over basic chatbots
- [ ] Interest in automotive industry applications
- [ ] Questions about customization for specific business needs

---

## 🔧 Troubleshooting Guide

### **If Agents Don't Route Correctly:**
- Check Azure OpenAI API connectivity
- Verify environment variables
- Clear chat history and try again
- Use more specific keywords in queries

### **If Document Search Returns No Results:**
- Confirm documents are uploaded and processed
- Check ChromaDB database statistics
- Try broader search terms
- Verify vector database is not empty

### **If News Search Fails:**
- Check internet connectivity
- Verify external API availability
- Try alternative news-related queries
- Show cached/example responses if needed

---

## 🎪 Interactive Demo Ideas

### **Audience Participation:**
1. **"Design Your Dream Car Query"**: Let audience suggest specific requirements
2. **"Stumping the AI"**: Try edge cases and unusual requests
3. **"Before/After Comparison"**: Show simple vs. sophisticated recommendations
4. **"Architecture Deep Dive"**: Explain technical components based on audience technical level

### **Extended Demo Scenarios:**
- **Fleet Management**: Multiple car recommendations for business fleet
- **Comparison Analysis**: Direct comparison between specific models
- **Maintenance Planning**: Information retrieval for service schedules
- **Market Research**: News trends affecting automotive decisions

---

*This demo script showcases the full capabilities of your automotive chatbot, demonstrating both the user experience and the sophisticated technical architecture underneath. Adjust timing and depth based on your audience's technical background and interests.*
