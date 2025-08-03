import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiService } from '../services/apiService'
import { 
  BarChart3, 
  Download, 
  FileText, 
  Eye,
  Brain,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader2,
  ArrowLeft
} from 'lucide-react'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const ModelResults = () => {
  const { id } = useParams()
  const [modelData, setModelData] = useState(null)
  const [insights, setInsights] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchModelResults()
  }, [id])

  const fetchModelResults = async () => {
    try {
      const [modelResults, summary] = await Promise.all([
        apiService.getModelResults(id),
        apiService.getModelSummary(id)
      ])
      
      setModelData(modelResults)
      setInsights(summary.insights || '')
    } catch (err) {
      setError('Failed to load model results')
      console.error('Error fetching model results:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPdf = async () => {
    try {
      const blob = await apiService.downloadPdfReport(id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `insightai_report_${id}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading PDF:', error)
    }
  }

  const handleDownloadCsv = async () => {
    try {
      const blob = await apiService.downloadCsvResults(id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `insightai_results_${id}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading CSV:', error)
    }
  }

  const getMetricsChartData = () => {
    if (!modelData?.metrics) return null

    const metrics = modelData.metrics
    const taskType = modelData.model?.task_type

    if (taskType === 'classification') {
      return {
        labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
        datasets: [{
          label: 'Performance Metrics',
          data: [
            metrics.accuracy || 0,
            metrics.precision || 0,
            metrics.recall || 0,
            metrics.f1_score || 0
          ],
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 1
        }]
      }
    } else if (taskType === 'regression') {
      return {
        labels: ['R² Score', 'RMSE', 'MAE'],
        datasets: [{
          label: 'Performance Metrics',
          data: [
            metrics.r2_score || 0,
            metrics.rmse || 0,
            metrics.mae || 0
          ],
          backgroundColor: 'rgba(34, 197, 94, 0.8)',
          borderColor: 'rgba(34, 197, 94, 1)',
          borderWidth: 1
        }]
      }
    }

    return null
  }

  const getConfusionMatrixData = () => {
    if (!modelData?.metrics?.confusion_matrix) return null

    const cm = modelData.metrics.confusion_matrix
    return {
      labels: ['Predicted Negative', 'Predicted Positive'],
      datasets: [{
        label: 'Actual Negative',
        data: [cm[0][0], cm[0][1]],
        backgroundColor: 'rgba(239, 68, 68, 0.8)'
      }, {
        label: 'Actual Positive',
        data: [cm[1][0], cm[1][1]],
        backgroundColor: 'rgba(34, 197, 94, 0.8)'
      }]
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Error Loading Results
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mb-4">{error}</p>
        <Link to="/models" className="btn-primary">
          Back to Models
        </Link>
      </div>
    )
  }

  if (!modelData) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Model not found
        </h3>
        <Link to="/models" className="btn-primary">
          Back to Models
        </Link>
      </div>
    )
  }

  const model = modelData.model
  const metrics = modelData.metrics

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/models" className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <ArrowLeft className="h-6 w-6" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{model.name}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {model.task_type} • {model.algorithm} • {new Date(model.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleDownloadPdf}
            className="btn-secondary flex items-center"
          >
            <FileText className="h-4 w-4 mr-2" />
            PDF Report
          </button>
          <button
            onClick={handleDownloadCsv}
            className="btn-secondary flex items-center"
          >
            <Download className="h-4 w-4 mr-2" />
            CSV Results
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'insights', 'charts', 'details'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Model Info */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Model Information
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Task Type:</span>
                  <span className="text-gray-900 dark:text-white capitalize">{model.task_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Algorithm:</span>
                  <span className="text-gray-900 dark:text-white">{model.algorithm}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Target Column:</span>
                  <span className="text-gray-900 dark:text-white">{model.target_column || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Features Used:</span>
                  <span className="text-gray-900 dark:text-white">{model.feature_columns?.length || 0}</span>
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Performance Metrics
              </h3>
              <div className="space-y-3">
                {Object.entries(metrics).map(([key, value]) => {
                  if (typeof value === 'number') {
                    return (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400 capitalize">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-gray-900 dark:text-white font-medium">
                          {value.toFixed(4)}
                        </span>
                      </div>
                    )
                  }
                  return null
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="card p-6">
            <div className="flex items-center mb-4">
              <Brain className="h-6 w-6 text-primary-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                AI-Generated Insights
              </h3>
            </div>
            <div className="prose prose-gray dark:prose-invert max-w-none">
              <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                {insights || 'No insights available for this model.'}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'charts' && (
          <div className="space-y-6">
            {/* Performance Metrics Chart */}
            {getMetricsChartData() && (
              <div className="card p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Performance Metrics
                </h3>
                <div className="h-64">
                  <Bar
                    data={getMetricsChartData()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 1,
                          ticks: {
                            color: '#6B7280'
                          }
                        },
                        x: {
                          ticks: {
                            color: '#6B7280'
                          }
                        }
                      },
                      plugins: {
                        legend: {
                          labels: {
                            color: '#6B7280'
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            )}

            {/* Confusion Matrix */}
            {getConfusionMatrixData() && (
              <div className="card p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Confusion Matrix
                </h3>
                <div className="h-64">
                  <Doughnut
                    data={getConfusionMatrixData()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                          labels: {
                            color: '#6B7280'
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'details' && (
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Model Details
            </h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Feature Columns</h4>
                <div className="flex flex-wrap gap-2">
                  {model.feature_columns?.map((feature) => (
                    <span
                      key={feature}
                      className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded"
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Model Parameters</h4>
                <pre className="bg-gray-50 dark:bg-gray-800 p-4 rounded text-sm overflow-x-auto">
                  {JSON.stringify(model.parameters || {}, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ModelResults 