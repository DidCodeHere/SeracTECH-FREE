import React, { useState } from 'react';
import Papa from 'papaparse';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface PlanningApplication {
  id: string;
  desc: string;
  addr: string;
  postcode: string;
  date_received: string;
  status: string;
  link: string;
}

interface ExportButtonProps {
  data: PlanningApplication[];
}

export const ExportButton: React.FC<ExportButtonProps> = ({ data }) => {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportCSV = () => {
    setIsExporting(true);
    try {
      const csv = Papa.unparse(data);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `planning_leads_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Export failed', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPDF = () => {
    setIsExporting(true);
    try {
      const doc = new jsPDF();
      
      doc.text("Planning Applications Lead List", 14, 15);
      doc.setFontSize(10);
      doc.text(`Generated on ${new Date().toLocaleDateString()}`, 14, 22);

      const tableData = data.map(row => [
        row.id,
        row.desc.substring(0, 50) + (row.desc.length > 50 ? '...' : ''),
        row.addr,
        row.postcode,
        row.date_received
      ]);

      autoTable(doc, {
        head: [['Ref', 'Description', 'Address', 'Postcode', 'Date']],
        body: tableData,
        startY: 25,
        styles: { fontSize: 8 },
        columnStyles: {
          0: { cellWidth: 25 },
          1: { cellWidth: 60 },
          2: { cellWidth: 50 },
          3: { cellWidth: 20 },
          4: { cellWidth: 25 }
        }
      });

      doc.save(`planning_leads_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error('Export failed', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="flex gap-2 mt-4">
      <button
        onClick={handleExportCSV}
        disabled={isExporting}
        className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors disabled:opacity-50"
      >
        {isExporting ? 'Exporting...' : 'Download CSV'}
      </button>
      <button
        onClick={handleExportPDF}
        disabled={isExporting}
        className="px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors disabled:opacity-50"
      >
        {isExporting ? 'Exporting...' : 'Download PDF'}
      </button>
    </div>
  );
};
