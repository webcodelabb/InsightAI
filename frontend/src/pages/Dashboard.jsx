import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiService } from '../services/apiService'
import { 
  Upload, 
  BarChart3, 
  FileText, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react'

const Dashboard = () => {
  const [stats, setStats] = useState({
    datasets: 0,
    models: 0,
    totalRows: 0,
    totalColumns: 0
  })
  const [recentDatasets, setRecentDatasets] = useState([])
  const [recentModels, setRecentModels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [datasets, models] = await Promise.all([
          apiService.getDatasets(),
          apiService.getModels()
        ])

        const totalRows = datasets.reduce((sum, dataset) => sum + dataset.row_count, 0)
        const totalColumns = datasets.reduce((sum, dataset) => sum + dataset.column_count, 0)

        setStats({
          datasets: datasets.length,
          models: models.length,
          totalRows,
          totalColumns
        })

        setRecentDatasets(datasets.slice(0, 5))
        setRecentModels(models.slice(0, 5))
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Welcome to InsightAI. Upload your data and start generating insights.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileText className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  Total Datasets
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  {stats.datasets}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BarChart3 className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  Trained Models
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  {stats.models}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  Total Rows
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  {stats.totalRows.toLocaleString()}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Upload className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                  Total Columns
                </dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">
                  {stats.totalColumns}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            to="/upload"
            className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <Upload className="h-6 w-6 text-primary-600 mr-3" />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Upload Dataset</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">Add new CSV data</p>
            </div>
          </Link>

          <Link
            to="/models"
            className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <BarChart3 className="h-6 w-6 text-green-600 mr-3" />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Train Model</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">Start ML analysis</p>
            </div>
          </Link>

          <div className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <FileText className="h-6 w-6 text-blue-600 mr-3" />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">View Reports</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">Download insights</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Datasets */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Recent Datasets
          </h3>
          <div className="space-y-4">
            {recentDatasets.length > 0 ? (
              recentDatasets.map((dataset) => (
                <div key={dataset.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-primary-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {dataset.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {dataset.row_count} rows • {dataset.column_count} columns
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(dataset.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <FileText className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No datasets uploaded yet
                </p>
                <Link
                  to="/upload"
                  className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400"
                >
                  Upload your first dataset
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Recent Models */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Recent Models
          </h3>
          <div className="space-y-4">
            {recentModels.length > 0 ? (
              recentModels.map((model) => (
                <div key={model.id} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-green-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {model.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {model.task_type} • {model.algorithm}
                      </p>
                    </div>
                  </div>
                  <Link
                    to={`/models/${model.id}`}
                    className="text-xs text-primary-600 hover:text-primary-500 dark:text-primary-400"
                  >
                    View Results
                  </Link>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <BarChart3 className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No models trained yet
                </p>
                <Link
                  to="/models"
                  className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400"
                >
                  Train your first model
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 