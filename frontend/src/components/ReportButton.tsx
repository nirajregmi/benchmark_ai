
import React, { useState } from 'react';
import { FileText, Download, Loader2 } from 'lucide-react';
import { downloadReport } from '../services/api';

interface ReportButtonProps {
    selectedPods: string[];
}

export const ReportButton: React.FC<ReportButtonProps> = ({ selectedPods }) => {
    const [loading, setLoading] = useState(false);

    const handleDownload = async () => {
        if (selectedPods.length < 2) return;

        setLoading(true);
        try {
            await downloadReport(selectedPods);
        } catch (err) {
            console.error(err);
            alert("Failed to generate report. Details in console.");
        } finally {
            setLoading(false);
        }
    };

    const isDisabled = selectedPods.length < 2 || loading;

    return (
        <button
            onClick={handleDownload}
            disabled={isDisabled}
            className={`
                flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all
                ${isDisabled
                    ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'}
            `}
            title={selectedPods.length < 2 ? "Select at least 2 pods to generate a report" : "Generate Comparison Report"}
        >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
            <span>{loading ? 'Generating...' : 'Report'}</span>
            {!loading && !isDisabled && <Download size={14} className="opacity-70" />}
        </button>
    );
};
