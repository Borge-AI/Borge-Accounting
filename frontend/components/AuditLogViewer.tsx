'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'

interface AuditLogViewerProps {
  onClose: () => void
}

interface AuditLog {
  id: number
  user_id: number | null
  invoice_id: number | null
  action: string
  raw_ocr_output: string | null
  ai_prompt: string | null
  ai_response: string | null
  extra_data: string | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

export default function AuditLogViewer({ onClose }: AuditLogViewerProps) {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      const response = await api.get('/audit/')
      setLogs(response.data)
    } catch (error) {
      console.error('Failed to fetch audit logs:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">Loading audit logs...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold">Audit Logs</h2>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Close
          </button>
        </div>

        {logs.length === 0 ? (
          <p className="text-gray-600">No audit logs found.</p>
        ) : (
          <div className="space-y-4">
            {logs.map((log) => (
              <div
                key={log.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedLog(log)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{log.action}</p>
                    <p className="text-sm text-gray-600">
                      Invoice #{log.invoice_id} • {new Date(log.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-sm text-gray-500">
                    User #{log.user_id}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedLog && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">Audit Log Details</h3>
            <button
              onClick={() => setSelectedLog(null)}
              className="text-gray-600 hover:text-gray-800"
            >
              Close
            </button>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Action</label>
              <p className="mt-1">{selectedLog.action}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Timestamp</label>
              <p className="mt-1">{new Date(selectedLog.created_at).toLocaleString()}</p>
            </div>
            {selectedLog.raw_ocr_output && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">OCR Output</label>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40">
                  {selectedLog.raw_ocr_output}
                </pre>
              </div>
            )}
            {selectedLog.ai_prompt && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">AI Prompt</label>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40">
                  {selectedLog.ai_prompt}
                </pre>
              </div>
            )}
            {selectedLog.ai_response && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">AI Response</label>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40">
                  {selectedLog.ai_response}
                </pre>
              </div>
            )}
            {selectedLog.extra_data && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Metadata</label>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40">
                  {selectedLog.extra_data}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
