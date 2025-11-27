# 🚀 TaskFlow Agent - Workflow Templates Guide

## ✅ Fixed Issues
- **422 Unprocessable Entity Error**: Fixed by removing `workflow_id` from request body (it's already in the URL path)
- Workflow execution now works correctly with proper schema validation

## 🎯 Available Workflow Templates

### 1. 📧 Email Summarizer
**Use Case**: Automatically analyze and summarize incoming emails

**Nodes**:
1. **Extractor** - Extracts sender, subject, date, main topic, key points, action items
2. **Analyzer** - Determines priority (High/Medium/Low), category, sentiment
3. **Writer** - Generates professional 2-3 sentence summary

**Example Input**: 
```
From: john@company.com
Subject: Urgent: Q4 Report Deadline
Hi team, we need to submit the Q4 financial report by Friday...
```

**Output**: Professional summary with priority and action items

---

### 2. ✍️ Content Generator
**Use Case**: Research and write articles, blog posts, or content

**Nodes**:
1. **Researcher** - Gathers key information, facts, and relevant details
2. **Writer** - Creates comprehensive article with intro, main points, conclusion

**Example Input**: 
```
Topic: The Future of AI in Healthcare
```

**Output**: Well-structured article with research-backed content

---

### 3. 📊 Data Analyzer
**Use Case**: Extract, analyze, and report on data patterns

**Nodes**:
1. **Extractor** - Structures data from text or documents
2. **Analyzer** - Identifies patterns, trends, anomalies, key insights
3. **Writer** - Creates actionable report with recommendations

**Example Input**: 
```
Sales data for Q3 2025: Product A: $150k, Product B: $89k...
```

**Output**: Analysis report with trends and recommendations

---

### 4. 💬 Customer Support Assistant
**Use Case**: Analyze customer inquiries and generate responses

**Nodes**:
1. **Analyzer** - Understands issue type, urgency, sentiment, required expertise
2. **Writer** - Generates professional, empathetic response with solutions

**Example Input**: 
```
Customer: I can't log into my account after the update!
```

**Output**: Professional support response with troubleshooting steps

---

### 5. 📝 Meeting Notes Generator
**Use Case**: Convert meeting transcripts into structured notes

**Nodes**:
1. **Extractor** - Extracts attendees, topics, decisions, action items, deadlines
2. **Writer** - Creates structured notes with summary and action items table

**Example Input**: 
```
Meeting transcript: John discussed the new project timeline...
```

**Output**: Formatted meeting notes with action items table

---

### 6. 👨‍💻 Code Reviewer
**Use Case**: Review code and provide improvement suggestions

**Nodes**:
1. **Analyzer** - Checks for bugs, security issues, performance problems, best practices
2. **Writer** - Generates detailed review with specific suggestions and code examples

**Example Input**: 
```python
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
```

**Output**: Code review with suggestions for improvement

---

## 🎨 How to Use Templates

### Creating a Workflow from Template:

1. **Navigate to Create Workflow**
   - Go to `/workflows/create`
   - Or click "Create Workflow" from dashboard

2. **Select Template**
   - Choose from dropdown: "Workflow Template"
   - Select one of the 6 available templates
   - Or choose "Blank Workflow" to build from scratch

3. **Fill in Details**
   - Enter workflow name (e.g., "My Email Summarizer")
   - Add description
   - Choose trigger type (Manual recommended for testing)

4. **Create**
   - Click "Create Workflow"
   - You'll be redirected to the editor with pre-configured nodes

5. **Customize (Optional)**
   - Modify node prompts to fit your needs
   - Add or remove nodes
   - Adjust configurations

6. **Test**
   - Scroll to "Test Workflow" section
   - Paste test input
   - Click "Run Test"
   - View execution results

7. **Save & Use**
   - Click "Save" to save your changes
   - Go to workflows list
   - Click "Run" to execute with new data

---

## 🔧 Customizing Templates

### Modifying Node Prompts:
- Each node has a "Task/Prompt" field
- Edit to change what the AI agent does
- Use clear, specific instructions

### Connecting Nodes:
- Nodes automatically connect sequentially
- Use `{{node_X.output}}` to reference previous node outputs
- Example: `{{node_1.output}}` in node 2's input field

### Adding More Nodes:
- Click node type buttons (Extractor, Analyzer, Writer, Researcher)
- Configure the new node
- It automatically connects to the previous node

---

## 💡 Best Practices

1. **Clear Prompts**: Write specific, detailed prompts for each node
2. **Test Small**: Start with simple test inputs before complex data
3. **Iterate**: Adjust node prompts based on output quality
4. **Chain Logic**: Each node should build on the previous one's output
5. **Save Often**: Click save after making changes

---

## 🐛 Troubleshooting

### Issue: "422 Unprocessable Entity"
✅ **Fixed**: This error has been resolved. Workflow execution now works properly.

### Issue: Workflow not executing
- Check that all nodes have prompts configured
- Ensure workflow is saved before testing
- Verify test input is provided

### Issue: Poor quality output
- Make node prompts more specific
- Add more context to instructions
- Consider adding intermediate nodes for complex tasks

---

## 🎯 Next Steps

1. **Create your first workflow** from a template
2. **Test it** with sample data
3. **Customize** node prompts to fit your use case
4. **Save and run** on real data
5. **Share** your workflow configurations with team

---

## 📚 Template Comparison

| Template | Nodes | Complexity | Best For |
|----------|-------|------------|----------|
| Email Summarizer | 3 | Medium | Email triage, inbox management |
| Content Generator | 2 | Low | Blog posts, articles, content creation |
| Data Analyzer | 3 | Medium | Reports, insights, data interpretation |
| Customer Support | 2 | Low | Support tickets, FAQ responses |
| Meeting Notes | 2 | Low | Meeting summaries, action tracking |
| Code Reviewer | 2 | Medium | Code quality, peer review automation |

---

## 🚀 Advanced Usage

### Creating Custom Templates:
1. Build a workflow manually with your desired nodes
2. Test and refine it
3. Save the configuration
4. Reuse by copying node setup to new workflows

### Combining Templates:
- Mix nodes from different templates
- Create hybrid workflows (e.g., extract + analyze + research + write)
- Build complex multi-step automation pipelines

---

**Happy Automating! 🎉**
