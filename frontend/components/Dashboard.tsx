'use client'

import { useState, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import api from '@/lib/api'
import InvoiceUpload from './InvoiceUpload'
import InvoiceList from './InvoiceList'
import InvoiceDetail from './InvoiceDetail'
import AuditLogViewer from './AuditLogViewer'

interface Invoice {
  id: number
  filename: string
  file_size: number
  status: string
  created_at: string
}

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [selectedInvoice, setSelectedInvoice] = useState<number | null>(null)
  const [showAuditLogs, setShowAuditLogs] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInvoices()
  }, [])

  const fetchInvoices = async () => {
    try {
      const response = await api.get('/invoices/')
      setInvoices(response.data)
    } catch (error) {
      console.error('Failed to fetch invoices:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInvoiceUploaded = () => {
    fetchInvoices()
  }

  const handleInvoiceSelect = (invoiceId: number) => {
    setSelectedInvoice(invoiceId)
  }

  const handleBackToList = () => {
    setSelectedInvoice(null)
    fetchInvoices()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Accounting Assistant</h1>
              <p className="text-sm text-gray-600">{user?.full_name} ({user?.role})</p>
            </div>
            <div className="flex items-center space-x-4">
              {user?.role === 'admin' && (
                <button
                  onClick={() => setShowAuditLogs(!showAuditLogs)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  {showAuditLogs ? 'Hide' : 'Show'} Audit Logs
                </button>
              )}
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showAuditLogs ? (
          <AuditLogViewer onClose={() => setShowAuditLogs(false)} />
        ) : selectedInvoice ? (
          <InvoiceDetail invoiceId={selectedInvoice} onBack={handleBackToList} />
        ) : (
          <div className="space-y-6">
            <InvoiceUpload onUploaded={handleInvoiceUploaded} />
            <InvoiceList invoices={invoices} onSelect={handleInvoiceSelect} loading={loading} />
          </div>
        )}
      </main>
    </div>
  )
}
