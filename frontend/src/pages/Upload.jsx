import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { apiService } from '../services/apiService'
import { 
  Upload as UploadIcon, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Eye,
  Download
} from 'lucide-react'

const Upload = () => {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [error, setError] = useState('')
  const [datasetPreview, setDatasetPreview] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file && file.type === 'text/csv') {
      setUploadedFile(file)
      setError('')
      setUploadSuccess(false)
    } else {
      setError('Please upload a valid CSV file')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  })

  const handleUpload = async () => {
    if (!uploadedFile) return

    setUploading(true)
    setError('')

    try {
      const result = await apiService.uploadDataset(uploadedFile)
      setUploadSuccess(true)
      setDatasetPreview(result)
      
      // Reset form after successful upload
      setTimeout(() => {
        setUploadedFile(null)
        setUploadSuccess(false)
        setDatasetPreview(null)
      }, 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const removeFile = () => {
    setUploadedFile(null)
    setError('')
    setUploadSuccess(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Dataset</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Upload your CSV file to start analyzing your data with AI-powered insights.
        </p>
      </div>

      {/* Upload Area */}
      <div className="card p-8">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
          }`}
        >
          <input {...getInputProps()} />
          <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <p className="text-lg font-medium text-gray-900 dark:text-white">
              {isDragActive ? 'Drop your CSV file here' : 'Drag and drop your CSV file here'}
            </p>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              or click to browse files
            </p>
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Maximum file size: 10MB
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <p className="ml-3 text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {uploadSuccess && (
          <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <p className="ml-3 text-sm text-green-600 dark:text-green-400">
                Dataset uploaded successfully!
              </p>
            </div>
          </div>
        )}

        {/* File Preview */}
        {uploadedFile && (
          <div className="mt-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-primary-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {uploadedFile.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={removeFile}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="mt-4 w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <div className="flex items-center justify-center">
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  Uploading...
                </div>
              ) : (
                'Upload Dataset'
              )}
            </button>
          </div>
        )}
      </div>

      {/* Dataset Preview */}
      {datasetPreview && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Dataset Preview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Dataset Info</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Name:</span>
                  <span className="text-gray-900 dark:text-white">{datasetPreview.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Rows:</span>
                  <span className="text-gray-900 dark:text-white">{datasetPreview.row_count.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Columns:</span>
                  <span className="text-gray-900 dark:text-white">{datasetPreview.column_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">File Size:</span>
                  <span className="text-gray-900 dark:text-white">
                    {(datasetPreview.file_size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Column Types</h4>
              <div className="space-y-2 text-sm">
                {Object.entries(datasetPreview.column_info || {}).map(([column, info]) => (
                  <div key={column} className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">{column}:</span>
                    <span className="text-gray-900 dark:text-white capitalize">{info.type}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Upload Guidelines
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Supported Formats</h4>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• CSV files only</li>
              <li>• Maximum file size: 10MB</li>
              <li>• UTF-8 encoding recommended</li>
              <li>• First row should contain column headers</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Data Requirements</h4>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• At least 10 rows of data</li>
              <li>• Mix of numeric and categorical columns</li>
              <li>• Clean, consistent data format</li>
              <li>• No sensitive personal information</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Upload 