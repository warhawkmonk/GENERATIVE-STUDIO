---
title: Generative Studio
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
- ai
- generative
- llm
- image-generation
pinned: false
short_description: An AI-powered generative studio with LLM, image generation, and data analysis capabilities
license: mit
---

# Generative Studio

A comprehensive generative AI application built with **Streamlit** that combines Large Language Models, image generation, PDF processing, and intelligent data analysis in one unified interface.

## 🌟 Features

### AI & Language Models
- **LLM Integration**: Powered by Groq API for fast AI responses
- **Question Answering**: Built-in Q&A pipeline for document analysis
- **Text Embeddings**: Semantic search using SentenceTransformers
- **Code Generation & Execution**: AI-powered code generation with automatic error correction

### Image Processing
- **Image Generation**: Powered by Diffusers library with inpainting support
- **Image Manipulation**: Drawing canvas for interactive editing
- **Image Processing**: Advanced CV capabilities with OpenCV
- **Batch Processing**: Handle multiple images efficiently

### Document Processing
- **PDF Handling**: Read and extract content from PDF files
- **Data Analysis**: Upload and analyze CSV/Excel files
- **Data Visualization**: Interactive charts and plots with Plotly and Seaborn

### Media & UI
- **Lottie Animations**: Smooth animated transitions and visual elements
- **Custom Navigation**: Navigation bar for seamless UX
- **Interactive Elements**: Modals, code editors, and custom components
- **File Management**: Database for storing records and messages

### Data Management
- **MongoDB Integration**: For scalable data persistence (optional)
- **Local Database**: JSON-based records for login, messages, and timestamps
- **Session State**: Persistent state management across pages

## 🚀 Quick Start

### Prerequisites
- Python 3.12.4 or higher
- Docker (optional, for containerized deployment)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GENERATIVE-STUDIO
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The application will be available at `http://localhost:8501`

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t generative-studio .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 generative-studio
   ```

   Access the app at `http://localhost:8501`

## 📋 Requirements

Key dependencies include:
- **Streamlit**: Web framework
- **Pandas & NumPy**: Data manipulation
- **PyTorch & Diffusers**: AI model support
- **Groq API**: LLM integration
- **Sentence Transformers**: Text embedding
- **OpenCV**: Image processing
- **Transformers**: NLP models
- **LangChain**: Document processing and text splitting
- **PyMuPDF & PyPDF2**: PDF handling
- **Plotly & Seaborn**: Data visualization
- **Streamlit Components**: Enhanced UI (navigation, modals, canvas, etc.)

See [requirements.txt](requirements.txt) for the complete list.

## 📁 Project Structure

```
GENERATIVE-STUDIO/
├── app.py                      # Main application entry point
├── src/
│   └── streamlit_app.py       # Alternative Streamlit app template
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── ALL_image_formation/        # Generated images and assets
│   ├── current_session_image.png
│   ├── home_screen.jpg
│   └── image_gen.png
├── lotte_animation_saver/      # Lottie animation JSON files
│   ├── animation_1.json
│   ├── animation_2.json
│   ├── animation_3.json
│   ├── animation_4.json
│   ├── animation_5.json
│   └── animation_6.json
├── DataBase/                   # Local data storage
│   ├── datetimeRecords.json
│   ├── login.json
│   └── message.json
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Configure the following environment variables as needed:

```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONUNBUFFERED=1
```

### API Configuration

Update the LLM API endpoint in `app.py`:
```python
url = "http://127.0.0.1:6000/api/llm-response"  # Modify as needed
```

## 🎯 Usage Examples

### Basic Text Generation
```python
# Send a prompt to the LLM
consume_llm_api_conditional(prompt="Your question here")
```

### Data Analysis
1. Upload a CSV or Excel file
2. Describe what analysis you want
3. The app generates and executes Python code automatically

### Image Generation & Inpainting
1. Upload an image or use the drawing canvas
2. The app uses diffusion models for generation and manipulation

### PDF Analysis
1. Upload a PDF file
2. Ask questions about the document content

## 🔑 Key Features Explanation

### Smart Code Execution
The application can automatically generate, execute, and fix Python code for data analysis with error correction through the LLM.

### Multi-Modal Processing
Handle text, images, PDFs, and data files in a unified interface with AI-powered insights.

### Streaming Responses
Real-time streaming of LLM responses for immediate feedback.

### Session Management
Persistent session state for maintaining context across interactions.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For questions, issues, or suggestions:
- Check the [Streamlit Documentation](https://docs.streamlit.io)
- Visit the [Streamlit Community Forums](https://discuss.streamlit.io)
- Review the [LangChain Documentation](https://python.langchain.com)
- Check [Diffusers Documentation](https://huggingface.co/docs/diffusers) for image generation features

## 🚀 Future Enhancements

- [ ] Enhanced model selection and customization
- [ ] Advanced batch processing for images
- [ ] Real-time collaboration features
- [ ] Extended export formats
- [ ] Performance optimization
- [ ] Mobile-friendly interface improvements
