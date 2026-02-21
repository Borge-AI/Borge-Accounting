'use client'

import { useState } from 'react'
import api from '@/lib/api'

interface Suggestion {
  id: number
  account_number: string
  vat_code: string
  confidence_score: number
  risk_level: string
  approval_status: string
  notes: string
}

interface SuggestionCardProps {
  suggestion: Suggestion
  invoiceId: number
  onUpdated: () => void
}

const riskColors: Record<string, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
}

export default function SuggestionCard({ suggestion, invoiceId, onUpdated }: SuggestionCardProps) {
  const [approving, setApproving] = useState(false)
  const [rejecting, setRejecting] = useState(false)
  const [notes, setNotes] = useState('')

  const handleApprove = async () => {
    setApproving(true)
    try {
      await api.post(`/suggestions/${suggestion.id}/approve`, {
        approved: true,
        notes: notes || undefined,
      })
      onUpdated()
    } catch (error) {
      console.error('Failed to approve:', error)
    } finally {
      setApproving(false)
    }
  }

  const handleReject = async () => {
    setRejecting(true)
    try {
      await api.post(`/suggestions/${suggestion.id}/approve`, {
        approved: false,
        notes: notes || undefined,
      })
      onUpdated()
    } catch (error) {
      console.error('Failed to reject:', error)
    } finally {
      setRejecting(false)
    }
  }

  const confidencePercentage = Math.round(suggestion.confidence_score * 100)
  const isProcessed = suggestion.approval_status !== 'pending'

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h4 className="text-lg font-semibold">Accounting Suggestion</h4>
          <p className="text-sm text-gray-600 mt-1">{suggestion.notes || 'No additional notes'}</p>
        </div>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            riskColors[suggestion.risk_level] || riskColors.medium
          }`}
        >
          {suggestion.risk_level.toUpperCase()} RISK
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Account Number</label>
          <p className="mt-1 text-lg font-semibold">{suggestion.account_number || 'N/A'}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">VAT Code</label>
          <p className="mt-1 text-lg font-semibold">{suggestion.vat_code || 'N/A'}</p>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <label className="block text-sm font-medium text-gray-700">Confidence Score</label>
          <span className="text-sm font-semibold">{confidencePercentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className={`h-2.5 rounded-full ${
              confidencePercentage >= 70
                ? 'bg-green-600'
                : confidencePercentage >= 50
                ? 'bg-yellow-600'
                : 'bg-red-600'
            }`}
            style={{ width: `${confidencePercentage}%` }}
          />
        </div>
      </div>

      {isProcessed && (
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <p className="text-sm">
            <span className="font-medium">Status:</span>{' '}
            <span className={suggestion.approval_status === 'approved' ? 'text-green-700' : 'text-red-700'}>
              {suggestion.approval_status.toUpperCase()}
            </span>
          </p>
        </div>
      )}

      {!isProcessed && (
        <div className="space-y-4">
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
              Notes (optional)
            </label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Add any notes about this decision..."
            />
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleApprove}
              disabled={approving || rejecting}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {approving ? 'Approving...' : 'Approve'}
            </button>
            <button
              onClick={handleReject}
              disabled={approving || rejecting}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {rejecting ? 'Rejecting...' : 'Reject'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
