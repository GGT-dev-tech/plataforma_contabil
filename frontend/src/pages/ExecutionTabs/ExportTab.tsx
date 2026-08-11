import React from 'react';
import { Download, FileSpreadsheet } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export const ExportTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const handleExport = () => {
    window.open(`/api/v1/executions/${executionId}/export`, '_blank');
  };

  return (
    <div className="flex justify-center items-center py-12">
      <div className="max-w-md w-full p-8 text-center bg-white border border-slate-200 shadow-sm rounded-xl">
        <div className="flex justify-center mb-6">
          <div className="bg-primary-50 p-4 rounded-full border border-primary-100">
            <FileSpreadsheet className="w-12 h-12 text-primary-600" />
          </div>
        </div>
        
        <h3 className="text-2xl font-bold text-slate-800 mb-2">Lote Contábil</h3>
        <p className="text-sm text-slate-500 mb-8">
          Todos os lançamentos gerados a partir das conciliações aprovadas estão prontos para serem importados no seu ERP Contábil (Domínio, Questor, Fortes).
        </p>
        
        <Button 
          size="lg" 
          onClick={handleExport}
          className="w-full text-base h-12 bg-primary-600 hover:bg-primary-700 text-white shadow-sm"
          leftIcon={<Download className="w-5 h-5" />}
        >
          Baixar CSV de Lançamentos
        </Button>
      </div>
    </div>
  );
};
