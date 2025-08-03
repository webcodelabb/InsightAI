import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiService } from '../services/apiService'
import { 
  BarChart3, 
  Plus, 
  Play, 
  Trash2, 
  Eye,
  Download,
  FileText,
  Loader2,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

const Models = () => {
  const [models, setModels] = useState([])
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showTrainingModal, setShowTrainingModal] = useState(false)
  const [trainingModel, setTrainingModel] = useState(false)
  const [selectedDataset, setSelectedDataset] = useState('')
  const [taskType, setTaskType] = useState('classification')
  const [targetColumn, setTargetColumn] = useState('')
  const [algorithm, setAlgorithm] = useState('auto')
  const [nClusters, setNClusters] = useState(3)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [modelsData, datasetsData] = await Promise.all([
        apiService.getModels(),
        apiService.getDatasets()
      ])
      setModels(modelsData)
      setDatasets(datasetsData)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTrainModel = async (e) => {
    e.preventDefault()
    if (!selectedDataset) {
      setError('Please select a dataset')
      return
    }

    if (taskType !== 'clustering' && !targetColumn) {
      setError('Please select a target column')
      return
    }

    setTrainingModel(true)
    setError('')

    try {
      const modelData = {
        dataset_id: parseInt(selectedDataset),
        task_type: taskType,
        target_column: targetColumn,
        algorithm: algorithm,
        n_clusters: nClusters
      }

      await apiService.trainModel(modelData)
      setShowTrainingModal(false)
      fetchData() // Refresh the models list
    } catch (err) {
      setError(err.response?.data?.detail || 'Training failed')
    } finally {
      setTrainingModel(false)
    }
  }

  const handleDeleteModel = async (modelId) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      try {
        await apiService.deleteModel(modelId)
        fetchData() // Refresh the models list
      } catch (error) {
        console.error('Error deleting model:', error)
      }
    }
  }

  const getTaskTypeColor = (type) => {
    switch (type) {
      case 'classification':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'regression':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'clustering':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Models</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Train and manage your machine learning models.
          </p>
        </div>
        <button
          onClick={() => setShowTrainingModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Train New Model
        </button>
      </div>

      {/* Models Grid */}
      {models.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {models.map((model) => (
            <div key={model.id} className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <BarChart3 className="h-8 w-8 text-primary-600 mr-3" />
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {model.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {model.algorithm}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTaskTypeColor(model.task_type)}`}>
                  {model.task_type}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Target:</span>
                  <span className="text-gray-900 dark:text-white">{model.target_column || 'N/A'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Features:</span>
                  <span className="text-gray-900 dark:text-white">{model.feature_columns?.length || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Created:</span>
                  <span className="text-gray-900 dark:text-white">
                    {new Date(model.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="flex space-x-2">
                <Link
                  to={`/models/${model.id}`}
                  className="flex-1 btn-secondary flex items-center justify-center text-sm"
                >
                  <Eye className="h-4 w-4 mr-1" />
                  View Results
                </Link>
                <button
                  onClick={() => handleDeleteModel(model.id)}
                  className="p-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No models yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Train your first model to start generating insights.
          </p>
          <button
            onClick={() => setShowTrainingModal(true)}
            className="btn-primary"
          >
            Train Your First Model
          </button>
        </div>
      )}

      {/* Training Modal */}
      {showTrainingModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Train New Model
            </h2>

            {error && (
              <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <p className="ml-3 text-sm text-red-600 dark:text-red-400">{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleTrainModel} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Dataset
                </label>
                <select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">Select a dataset</option>
                  {datasets.map((dataset) => (
                    <option key={dataset.id} value={dataset.id}>
                      {dataset.name} ({dataset.row_count} rows)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Task Type
                </label>
                <select
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="classification">Classification</option>
                  <option value="regression">Regression</option>
                  <option value="clustering">Clustering</option>
                </select>
              </div>

              {taskType !== 'clustering' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Target Column
                  </label>
                  <select
                    value={targetColumn}
                    onChange={(e) => setTargetColumn(e.target.value)}
                    className="input-field"
                    required
                  >
                    <option value="">Select target column</option>
                    {selectedDataset && datasets.find(d => d.id === parseInt(selectedDataset))?.column_info && 
                      Object.keys(datasets.find(d => d.id === parseInt(selectedDataset)).column_info).map((column) => (
                        <option key={column} value={column}>
                          {column}
                        </option>
                      ))
                    }
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Algorithm
                </label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="auto">Auto (Best Model)</option>
                  <option value="random_forest">Random Forest</option>
                  <option value="logistic_regression">Logistic Regression</option>
                  <option value="linear_regression">Linear Regression</option>
                  <option value="svm">Support Vector Machine</option>
                </select>
              </div>

              {taskType === 'clustering' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Number of Clusters
                  </label>
                  <input
                    type="number"
                    value={nClusters}
                    onChange={(e) => setNClusters(parseInt(e.target.value))}
                    min="2"
                    max="10"
                    className="input-field"
                  />
                </div>
              )}

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowTrainingModal(false)}
                  className="flex-1 btn-secondary"
                  disabled={trainingModel}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={trainingModel}
                  className="flex-1 btn-primary disabled:opacity-50"
                >
                  {trainingModel ? (
                    <div className="flex items-center justify-center">
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Training...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <Play className="h-4 w-4 mr-2" />
                      Train Model
                    </div>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Models 