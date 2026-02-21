'use client'

import { useState, useEffect } from 'react'
import api from '@/lib/api'
import SuggestionCard from './SuggestionCard'

interface InvoiceDetailProps {
  invoiceId: number
  onBack: () => void
}

interface Suggestion {
  id: number
  account_number: string
  vat_code: string
  confidence_score: number
  risk_level: string
  approval_status: string
  notes: string
  created_at: string
}

interface InvoiceDetail {
  id: number
  filename: string
  file_size: number
  status: string
  created_at: string
  suggestions: Suggestion[]
}

export default function InvoiceDetail({ invoiceId, onBack }: InvoiceDetailProps) {
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchInvoiceDetail()
    // Poll for updates if processing
    const interval = setInterval(() => {
      if (invoice?.status && ['processing', 'ocr_complete', 'ai_processing'].includes(invoice.status)) {
        fetchInvoiceDetail()
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [invoiceId])

  const fetchInvoiceDetail = async () => {
    try {
      const response = await api.get(`/invoices/${invoiceId}`)
      setInvoice(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load invoice')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">Loading invoice details...</p>
      </div>
    )
  }

  if (error || !invoice) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error || 'Invoice not found'}
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Back to List
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold">{invoice.filename}</h2>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Back to List
          </button>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Status:</span>
            <span className="ml-2 font-medium">{invoice.status}</span>
          </div>
          <div>
            <span className="text-gray-600">Uploaded:</span>
            <span className="ml-2 font-medium">{new Date(invoice.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {invoice.suggestions.length > 0 ? (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">AI Suggestions</h3>
          {invoice.suggestions.map((suggestion) => (
            <SuggestionCard
              key={suggestion.id}
              suggestion={suggestion}
              invoiceId={invoiceId}
              onUpdated={fetchInvoiceDetail}
            />
          ))}
        </div>
      ) : invoice.status === 'complete' ? (
        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-gray-600">No suggestions available.</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-gray-600">Processing invoice... This may take a few moments.</p>
        </div>
      )}
    </div>
  )
}
