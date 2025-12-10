import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { runSynthIdAudit } from '../services/complianceService';

const ComplianceCenterPage = () => {
  const [result, setResult] = useState(null);
  const mutation = useMutation(runSynthIdAudit, {
    onSuccess: (data) => {
      setResult(data);
      toast.success('Audit complete');
    },
    onError: (error) => toast.error(error.response?.data?.detail || 'Audit failed'),
  });

  return (
    <div className="p-6 space-y-4">
      <header>
        <h1 className="text-3xl font-bold text-white">Compliance Center</h1>
        <p className="text-gray-400">
          Run SynthID audits before every Release Flash milestone.
        </p>
      </header>

      <button
        onClick={() => mutation.mutate()}
        className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold"
        disabled={mutation.isLoading}
      >
        {mutation.isLoading ? 'Auditing…' : 'Run SynthID Audit'}
      </button>

      {result && (
        <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-6">
          <p className="text-white text-xl font-semibold">
            Issues detected: {result.issues}
          </p>
          <p className="text-gray-400 text-sm">
            A notification has been sent to Release Flash owners if any records are missing SynthID.
          </p>
        </div>
      )}
    </div>
  );
};

export default ComplianceCenterPage;

