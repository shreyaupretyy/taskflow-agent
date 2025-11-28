"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

export default function DocumentQAPage() {
  const [files, setFiles] = useState<FileList | null>(null)
  const [query, setQuery] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [documents, setDocuments] = useState<any[]>([])

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      alert('Please select files to upload')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      Array.from(files).forEach(file => {
        formData.append('files', file)
      })

      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        alert(`✅ Uploaded ${data.documents.length} document(s) with ${data.total_chunks} chunks`)
        setFiles(null)
        // Reset file input
        const fileInput = document.getElementById('file-upload') as HTMLInputElement
        if (fileInput) fileInput.value = ''
        loadDocuments()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail}`)
      }
    } catch (error) {
      alert('Failed to upload documents')
      console.error(error)
    } finally {
      setUploading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/documents/my-documents', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents)
      }
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) {
      alert('Please enter a question')
      return
    }

    setLoading(true)
    setResult('')

    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('query', query)

      const response = await fetch('http://localhost:8000/api/v1/documents/query', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        if (data.status === 'error') {
          setResult(data.message)
        } else {
          setResult(data.result.report || JSON.stringify(data.result, null, 2))
        }
      } else {
        const error = await response.json()
        setResult(`Error: ${error.detail}`)
      }
    } catch (error) {
      setResult('Failed to query documents')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Document Q&A (RAG)</h1>
          <p className="mt-2 text-gray-600">
            Upload documents and ask questions using Retrieval Augmented Generation
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Documents</CardTitle>
              <CardDescription>
                Upload PDF, text, or markdown files to create your knowledge base
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".txt,.md,.markdown,.pdf"
                  onChange={(e) => setFiles(e.target.files)}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
              </div>
              
              {files && files.length > 0 && (
                <div className="text-sm text-gray-600">
                  {files.length} file(s) selected
                </div>
              )}

              <Button 
                onClick={handleUpload}
                disabled={uploading || !files}
                className="w-full"
              >
                {uploading ? 'Uploading...' : 'Upload Documents'}
              </Button>

              <Button 
                variant="outline"
                onClick={loadDocuments}
                className="w-full"
              >
                Refresh Document List
              </Button>

              {documents.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h3 className="font-semibold text-sm">Uploaded Documents:</h3>
                  {documents.map(doc => (
                    <div key={doc.id} className="text-xs p-2 bg-gray-50 rounded">
                      <div className="font-medium">{doc.filename}</div>
                      <div className="text-gray-500">
                        {doc.chunk_count} chunks • {(doc.file_size / 1024).toFixed(1)} KB
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Query Section */}
          <Card>
            <CardHeader>
              <CardTitle>Ask Questions</CardTitle>
              <CardDescription>
                Query your uploaded documents with natural language
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={query}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
                placeholder="What are the main findings in the documents?"
                rows={6}
                className="resize-none"
              />

              <Button 
                onClick={handleQuery}
                disabled={loading || !query.trim()}
                className="w-full"
              >
                {loading ? 'Searching...' : 'Ask Question'}
              </Button>

              {result && (
                <div className="mt-4 p-4 bg-white border rounded-lg">
                  <h3 className="font-semibold mb-2">Answer:</h3>
                  <div className="whitespace-pre-wrap text-sm text-gray-700">
                    {result}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
