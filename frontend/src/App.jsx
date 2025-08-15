import { useState, useRef } from "react"
import {
  X,
  Upload,
  Sparkles,
  FileText,
  Loader2,
  Bot,
  Menu,
  Settings,
  Send
} from "lucide-react"

import { Button } from "./components/ui/button"
import { Textarea } from "./components/ui/textarea"
import { Badge } from "./components/ui/badge"
import { Progress } from "./components/ui/progress"
import {
  Card,
  CardHeader,
  CardContent,
  CardTitle
} from "./components/ui/card"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import Logo from "./assets/AIO.png"

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadLoading, setUploadLoading] = useState(false)
  const [statusMessage, setStatusMessage] = useState("Ready to assist you!")
  const [uploadStatus, setUploadStatus] = useState("")
  const [selectedFile, setSelectedFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState("")
  const [finalResponse, setFinalResponse] = useState("")
  const [synthesisBreakdown, setSynthesisBreakdown] = useState("")
  const [sourcesUsed, setSourcesUsed] = useState([])
  const [confidenceScore, setConfidenceScore] = useState(null)

  const fileInputRef = useRef(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }
  const handleDragLeave = () => setIsDragOver(false)
  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0])
      e.dataTransfer.clearData()
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
    setUploadStatus("")
    setError(null)
  }

  // Fixed upload function
  const handleUpload = async () => {
    if (!selectedFile || !query.trim()) {
      setError("Please select a file and enter a job description.")
      return
    }
    
    setUploadLoading(true)
    setLoading(true)
    setStatusMessage("Uploading & analyzing...")
    setError(null)
    setProgress(0)

    const formData = new FormData()
    formData.append("file", selectedFile)
    formData.append("job_description", query)

    try {
      const interval = setInterval(() => setProgress(p => Math.min(p + 10, 90)), 200)
      
      const res = await fetch("http://localhost:8000/analyze-resume", {
        method: "POST",
        body: formData,  // ✅ Fixed: Use 'body' not 'data'
        // Don't set Content-Type header - let browser set it automatically
      })
      
      clearInterval(interval)
      setProgress(100)

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
        console.error("Server error response:", errorData)
        throw new Error(errorData.detail || `Server returned ${res.status}: ${res.statusText}`)
      }

      const data = await res.json()
      const analysis = data.analysis
      
      // Update state with analysis results
      setFinalResponse(`**Fit Score:** ${analysis.overall_fit_score}/100\n\n${analysis.experience_gap}`)
      setSynthesisBreakdown(analysis.improvement_suggestions.map((s,i) => `${i+1}. ${s}`).join("\n"))
      setSourcesUsed(analysis.matching_skills || [])
      setConfidenceScore(analysis.confidence_score)
      setStatusMessage("Analysis complete!")
      setUploadStatus("Analysis completed successfully!")
      
    } catch (e) {
      console.error("Upload error details:", e)
      setError(e.message)
      setStatusMessage("Analysis failed.")
      setUploadStatus(`Error: ${e.message}`)
    } finally {
      setUploadLoading(false)
      setLoading(false)
      setTimeout(() => setProgress(0), 500)
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ""
    }
  }

  const handleSubmitQuery = async (e) => {
    e.preventDefault()
    if (selectedFile && query.trim()) {
      await handleUpload()
    } else {
      setError("Please upload a file and enter a job description to analyze.")
    }
  }

  const markdownComponents = {
    ul: ({ node, ...props }) => <ul {...props} />,
    ol: ({ node, ...props }) => <ol {...props} />,
    li: ({ node, ...props }) => <li {...props} />,
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out`}>
        
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <img src={Logo} alt="AIO Logo" className="w-8 h-8" />
            <h2 className="text-lg font-semibold text-gray-800">Turtle Techsai</h2>
          </div>
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* AI Status Card */}
        <Card className="border-none rounded-none">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="w-4 h-4 text-green-500" /> AI Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${loading ? "bg-yellow-400 animate-pulse" : "bg-green-400"}`}></div>
              <span className="text-sm font-medium text-gray-800">{statusMessage}</span>
            </div>
          </CardContent>
        </Card>

        {/* Upload Section */}
        <div className="p-4 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <Upload className="w-4 h-4" /> Document Upload
          </h3>

          <div
            className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              isDragOver ? "border-blue-400 bg-blue-50" : "border-gray-300 bg-gray-50"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
            <p className="text-sm font-medium text-gray-600 mb-1">Drag & drop files here</p>
            <p className="text-xs text-gray-500 mb-3">or click to browse</p>
            <p className="text-xs text-gray-400">PDF, DOC, TXT, Images up to 10MB</p>

            <input
              type="file"
              onChange={handleFileChange}
              ref={fileInputRef}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={uploadLoading}
              accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.bmp,.tiff,.tif"
            />
          </div>

          {/* Selected File */}
          {selectedFile && (
            <div className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs mt-2 gap-2">
              <div className="flex items-center gap-2 truncate">
                <FileText className="w-3 h-3 text-gray-500 flex-shrink-0" />
                <span className="text-gray-700 truncate">{selectedFile.name}</span>
                <span className="text-gray-500 shrink-0">
                  ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
              <button
                onClick={removeFile}
                className="text-red-500 hover:text-red-700"
                disabled={uploadLoading}
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          {progress > 0 && <Progress value={progress} className="h-1 mt-3" />}

          <Button
            onClick={handleUpload}
            disabled={uploadLoading || !selectedFile || !query.trim()}
            size="sm"
            className="w-full text-xs mt-3"
          >
            {uploadLoading ? (
              <>
                <Loader2 className="w-3 h-3 mr-1 animate-spin" /> Analyzing...
              </>
            ) : (
              <>
                <Upload className="w-3 h-3 mr-1" /> Analyze Resume
              </>
            )}
          </Button>

          {uploadStatus && (
            <div className={`text-xs p-2 rounded mt-2 ${
              uploadStatus.includes("Success") || uploadStatus.includes("completed")
                ? "bg-green-50 text-green-700"
                : uploadStatus.includes("Error")
                ? "bg-red-50 text-red-700"
                : "bg-blue-50 text-blue-700"
            }`}>
              {uploadStatus}
            </div>
          )}
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
              <Menu className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <img src={Logo} alt="AIO Logo" className="w-10 h-10 lg:hidden" />
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  Welcome to Resume Analyzer
                </h1>
                <p className="text-sm text-gray-600">Get the best compiled answers from multiple AI models.</p>
              </div>
            </div>
          </div>
          <Button variant="ghost" size="icon">
            <Settings className="w-5 h-5" />
          </Button>
        </header>

        {/* Main Area */}
        <main className="flex-1 flex flex-col overflow-auto p-6">
          <div className="max-w-4xl mx-auto flex-1 flex flex-col w-full">
            {finalResponse ? (
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="text-purple-600 w-5 h-5" /> AI Resume Analysis
                    {confidenceScore && <Badge className="ml-auto">{confidenceScore}</Badge>}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                    {finalResponse}
                  </ReactMarkdown>
                  {synthesisBreakdown && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <strong>Improvement Suggestions:</strong>
                      <div className="mt-2">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                          {synthesisBreakdown}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}
                  {sourcesUsed.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <strong>Matching Skills:</strong>
                      <ul className="list-disc list-inside mt-2">
                        {sourcesUsed.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <div className="text-center py-12 text-gray-600">
                <h2 className="text-2xl font-bold mb-2">Upload a resume and get AI insights</h2>
                <p>Use the sidebar to upload a resume PDF and enter a job description below.</p>
              </div>
            )}

            {/* Job Description Input */}
            <form onSubmit={handleSubmitQuery} className="mt-auto border-t border-gray-200 pt-4">
              <div className="flex gap-2 items-end">
                <Textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter the job description here..."
                  rows={3}
                  disabled={loading}
                  className="flex-1 resize-none"
                />
                <Button
                  type="submit"
                  disabled={loading || !query.trim() || !selectedFile}
                  className="flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  Analyze
                </Button>
              </div>
              {error && <p className="text-red-600 mt-2 text-sm">{error}</p>}
              <p className="text-xs text-gray-500 mt-1">
                Upload a resume file above and enter a job description to get AI-powered analysis.
              </p>
            </form>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
