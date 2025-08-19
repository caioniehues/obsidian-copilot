"""
Factory classes for generating vault-related test data.
Creates realistic vault documents, structures, and content for testing.
"""

import factory
from factory import Faker, LazyAttribute, SubFactory, LazyFunction
from typing import Dict, List, Any
import random
import hashlib


class VaultDocumentFactory(factory.Factory):
    """Factory for creating individual vault documents."""
    
    class Meta:
        model = dict
    
    # Basic document properties
    title = Faker("sentence", nb_words=4)
    path = LazyAttribute(lambda obj: f"{obj.title.lower().replace(' ', '-').replace('.', '')}.md")
    content = LazyAttribute(lambda obj: f"# {obj.title}\n\n{Faker('text', max_nb_chars=800).evaluate(None, None, {'locale': 'en_US'})}")
    
    # Metadata
    tags = factory.List([Faker("word") for _ in range(3)])
    created = Faker("date_time_this_year")
    modified = Faker("date_time_this_year")
    
    # RAG-specific fields
    chunks = LazyAttribute(lambda obj: [
        sentence.strip() for sentence in obj.content.split('.') 
        if len(sentence.strip()) > 10
    ][:5])  # Limit to 5 chunks for consistency


class TechnicalDocumentFactory(VaultDocumentFactory):
    """Factory for technical documentation."""
    
    title = factory.Iterator([
        "API Documentation",
        "System Architecture",
        "Database Schema",
        "Security Guidelines",
        "Performance Optimization",
        "Testing Strategy",
        "Deployment Guide",
        "Configuration Management"
    ])
    
    path = LazyAttribute(lambda obj: f"technical/{obj.title.lower().replace(' ', '-')}.md")
    
    content = LazyAttribute(lambda obj: f"""# {obj.title}

## Overview
{Faker('paragraph', nb_sentences=3).evaluate(None, None, {'locale': 'en_US'})}

## Key Components
- Component A: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
- Component B: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
- Component C: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

## Implementation Details
{Faker('paragraph', nb_sentences=5).evaluate(None, None, {'locale': 'en_US'})}

## Best Practices
1. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
2. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
3. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

## References
- [Documentation Link](https://example.com/docs)
- [API Reference](https://example.com/api)
""")
    
    tags = ["technical", "documentation", "engineering"]


class ProjectDocumentFactory(VaultDocumentFactory):
    """Factory for project-related documents."""
    
    title = factory.Iterator([
        "Project Roadmap",
        "Sprint Planning",
        "Feature Requirements",
        "Meeting Notes",
        "Project Status",
        "Risk Assessment",
        "Stakeholder Review",
        "Launch Plan"
    ])
    
    path = LazyAttribute(lambda obj: f"projects/{obj.title.lower().replace(' ', '-')}.md")
    
    content = LazyAttribute(lambda obj: f"""# {obj.title}

## Project: {Faker('company').evaluate(None, None, {'locale': 'en_US'})} Initiative

### Status: {random.choice(['Planning', 'In Progress', 'Review', 'Complete'])}

### Timeline
- Start Date: {Faker('date_this_year').evaluate(None, None, {'locale': 'en_US'})}
- Target Date: {Faker('future_date').evaluate(None, None, {'locale': 'en_US'})}

### Objectives
{Faker('paragraph', nb_sentences=4).evaluate(None, None, {'locale': 'en_US'})}

### Key Deliverables
1. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
2. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
3. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

### Risks and Mitigation
- Risk: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
- Mitigation: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

### Notes
{Faker('paragraph', nb_sentences=3).evaluate(None, None, {'locale': 'en_US'})}
""")
    
    tags = ["project", "planning", "management"]


class LearningDocumentFactory(VaultDocumentFactory):
    """Factory for learning and educational content."""
    
    title = factory.Iterator([
        "Machine Learning Fundamentals",
        "Python Best Practices",
        "Data Structures Overview",
        "Algorithm Analysis",
        "System Design Patterns",
        "Database Concepts",
        "Web Development Guide",
        "Security Principles"
    ])
    
    path = LazyAttribute(lambda obj: f"learning/{obj.title.lower().replace(' ', '-')}.md")
    
    content = LazyAttribute(lambda obj: f"""# {obj.title}

## Introduction
{Faker('paragraph', nb_sentences=2).evaluate(None, None, {'locale': 'en_US'})}

## Core Concepts

### Concept 1: {Faker('word').evaluate(None, None, {'locale': 'en_US'}).title()}
{Faker('paragraph', nb_sentences=3).evaluate(None, None, {'locale': 'en_US'})}

### Concept 2: {Faker('word').evaluate(None, None, {'locale': 'en_US'}).title()}
{Faker('paragraph', nb_sentences=3).evaluate(None, None, {'locale': 'en_US'})}

## Practical Applications
- Application 1: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
- Application 2: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
- Application 3: {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

## Key Takeaways
1. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
2. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
3. {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

## Further Reading
- [Resource 1](https://example.com/resource1)
- [Resource 2](https://example.com/resource2)
""")
    
    tags = ["learning", "education", "concepts"]


class CodeDocumentFactory(VaultDocumentFactory):
    """Factory for code and technical examples."""
    
    title = factory.Iterator([
        "Python Code Examples",
        "JavaScript Snippets",
        "SQL Queries",
        "API Integration Code",
        "Testing Examples",
        "Configuration Samples",
        "Utility Functions",
        "Error Handling Patterns"
    ])
    
    path = LazyAttribute(lambda obj: f"code/{obj.title.lower().replace(' ', '-')}.md")
    
    content = LazyAttribute(lambda obj: f"""# {obj.title}

## Overview
{Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}

## Example 1: Basic Implementation

```python
def example_function(param1, param2):
    '''
    {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
    '''
    result = param1 + param2
    return result

# Usage
result = example_function("Hello", "World")
print(result)
```

## Example 2: Advanced Usage

```python
class ExampleClass:
    def __init__(self, value):
        self.value = value
    
    def process(self):
        # {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
        return self.value * 2

# Usage
instance = ExampleClass(42)
processed = instance.process()
```

## Notes
{Faker('paragraph', nb_sentences=2).evaluate(None, None, {'locale': 'en_US'})}

## Best Practices
- {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
- {Faker('sentence').evaluate(None, None, {'locale': 'en_US'})}
""")
    
    tags = ["code", "examples", "programming"]


class VaultStructureFactory(factory.Factory):
    """Factory for creating complete vault structures."""
    
    class Meta:
        model = dict
    
    @classmethod
    def create_small_vault(cls) -> Dict[str, Any]:
        """Create a small vault with 10-15 documents."""
        documents = {}
        
        # Create different types of documents
        for _ in range(3):
            doc = TechnicalDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(3):
            doc = ProjectDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(4):
            doc = LearningDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(2):
            doc = CodeDocumentFactory()
            documents[doc["path"]] = doc
        
        # Add some generic documents
        for _ in range(3):
            doc = VaultDocumentFactory()
            documents[doc["path"]] = doc
        
        return documents
    
    @classmethod
    def create_medium_vault(cls) -> Dict[str, Any]:
        """Create a medium vault with 50-75 documents."""
        documents = {}
        
        # Create different types of documents in larger quantities
        for _ in range(15):
            doc = TechnicalDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(12):
            doc = ProjectDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(20):
            doc = LearningDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(10):
            doc = CodeDocumentFactory()
            documents[doc["path"]] = doc
        
        # Add generic documents
        for _ in range(8):
            doc = VaultDocumentFactory()
            documents[doc["path"]] = doc
        
        return documents
    
    @classmethod
    def create_large_vault(cls) -> Dict[str, Any]:
        """Create a large vault with 200+ documents."""
        documents = {}
        
        # Create different types of documents in large quantities
        for _ in range(60):
            doc = TechnicalDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(40):
            doc = ProjectDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(70):
            doc = LearningDocumentFactory()
            documents[doc["path"]] = doc
        
        for _ in range(30):
            doc = CodeDocumentFactory()
            documents[doc["path"]] = doc
        
        # Add generic documents
        for _ in range(25):
            doc = VaultDocumentFactory()
            documents[doc["path"]] = doc
        
        return documents
    
    @classmethod
    def create_specialized_vault(cls, domain: str) -> Dict[str, Any]:
        """Create a vault specialized for a specific domain."""
        documents = {}
        
        if domain == "machine_learning":
            topics = [
                "Neural Networks",
                "Deep Learning",
                "Supervised Learning",
                "Unsupervised Learning",
                "Reinforcement Learning",
                "Model Training",
                "Feature Engineering",
                "Model Evaluation",
                "Data Preprocessing",
                "MLOps"
            ]
            
            for topic in topics:
                doc = LearningDocumentFactory(title=topic)
                documents[doc["path"]] = doc
                
                # Add related code examples
                code_doc = CodeDocumentFactory(title=f"{topic} Code Examples")
                documents[code_doc["path"]] = code_doc
        
        elif domain == "web_development":
            topics = [
                "HTML Fundamentals",
                "CSS Styling",
                "JavaScript Basics",
                "React Components",
                "Node.js Backend",
                "Database Design",
                "API Development",
                "Testing Strategies",
                "Deployment",
                "Performance"
            ]
            
            for topic in topics:
                doc = LearningDocumentFactory(title=topic)
                documents[doc["path"]] = doc
                
                code_doc = CodeDocumentFactory(title=f"{topic} Examples")
                documents[code_doc["path"]] = code_doc
        
        return documents
    
    @classmethod
    def create_interconnected_vault(cls) -> Dict[str, Any]:
        """Create a vault with documents that reference each other."""
        documents = cls.create_medium_vault()
        
        # Add cross-references between documents
        doc_paths = list(documents.keys())
        
        for path, doc in documents.items():
            # Add references to other documents
            if random.random() < 0.3:  # 30% chance of having references
                reference_count = random.randint(1, 3)
                referenced_docs = random.sample(
                    [p for p in doc_paths if p != path], 
                    min(reference_count, len(doc_paths) - 1)
                )
                
                reference_text = "\n\n## Related Documents\n"
                for ref_path in referenced_docs:
                    ref_doc = documents[ref_path]
                    reference_text += f"- [[{ref_doc['title']}]]\n"
                
                doc["content"] += reference_text
        
        return documents


class DocumentVariationFactory:
    """Factory for creating document variations and edge cases."""
    
    @staticmethod
    def create_empty_document() -> Dict[str, Any]:
        """Create an empty document."""
        return VaultDocumentFactory(
            content="",
            chunks=[],
            tags=[]
        )
    
    @staticmethod
    def create_large_document() -> Dict[str, Any]:
        """Create a very large document."""
        content = "# Large Document\n\n"
        for i in range(50):
            content += f"## Section {i+1}\n\n"
            content += Faker("paragraph", nb_sentences=10).evaluate(None, None, {'locale': 'en_US'})
            content += "\n\n"
        
        return VaultDocumentFactory(
            title="Large Test Document",
            content=content,
            path="large/big-document.md",
            tags=["large", "test", "performance"]
        )
    
    @staticmethod
    def create_document_with_special_characters() -> Dict[str, Any]:
        """Create document with special characters and Unicode."""
        content = """# Special Characters Document

This document contains various special characters:

## Unicode Characters
- Emoji: 🚀 💡 🎯 📚 ⚡ 🔥
- Mathematical: α β γ Δ Σ ∑ ∫ ∇ ∞
- Accented: café naïve résumé piñata

## Code Examples
```python
# Unicode in code
greeting = "Hello, 世界! 🌍"
math_symbols = "α + β = γ"
```

## Markdown Special Cases
- **Bold with 中文**
- *Italics with العربية*
- `Code with русский`

## Edge Cases
- Zero-width characters: ‌‍
- Right-to-left: מימין לשמאל
- Combining characters: é (e + ´)
"""
        
        return VaultDocumentFactory(
            title="Special Characters Test",
            content=content,
            path="test/special-characters.md",
            tags=["unicode", "special", "test"]
        )
    
    @staticmethod
    def create_malformed_document() -> Dict[str, Any]:
        """Create document with potential parsing issues."""
        content = """# Malformed Document

## Unclosed Code Block
```python
def broken_function():
    return "missing closing quote

## Mismatched Brackets
[Link with unclosed bracket(https://example.com

## Invalid Markdown
### ### Double hash
**bold without closing

## HTML in Markdown
<script>alert('test')</script>
<div class="unclosed-div">

## Strange Characters
Control chars: \x00\x01\x02
"""
        
        return VaultDocumentFactory(
            title="Malformed Test Document",
            content=content,
            path="test/malformed.md",
            tags=["malformed", "test", "edge-case"]
        )