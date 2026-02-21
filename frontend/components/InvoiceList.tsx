'use client'

import { format } from 'date-fns'

interface Invoice {
  id: number
  filename: string
  file_size: number
  status: string
  created_at: string
}

interface InvoiceListProps {
  invoices: Invoice[]
  onSelect: (invoiceId: number) => void
  loading: boolean
}

const statusColors: Record<string, string> = {
  uploaded: 'bg-gray-100 text-gray-800',
  processing: 'bg-yellow-100 text-yellow-800',
  ocr_complete: 'bg-blue-100 text-blue-800',
  ai_processing: 'bg-purple-100 text-purple-800',
  complete: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
}

export default function InvoiceList({ invoices, onSelect, loading }: InvoiceListProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">Loading invoices...</p>
      </div>
    )
  }

  if (invoices.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">No invoices uploaded yet.</p>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold">Invoices</h2>
      </div>
      <div className="divide-y divide-gray-200">
        {invoices.map((invoice) => (
          <div
            key={invoice.id}
            onClick={() => onSelect(invoice.id)}
            className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{invoice.filename}</p>
                <p className="text-sm text-gray-500">
                  {formatFileSize(invoice.file_size)} • {format(new Date(invoice.created_at), 'PPp')}
                </p>
              </div>
              <div className="ml-4">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    statusColors[invoice.status] || statusColors.uploaded
                  }`}
                >
                  {invoice.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
