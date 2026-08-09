import React from 'react';
import { Download, FileSpreadsheet } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { GlassCard } from '../../components/ui/GlassCard';

export const ExportTab: React.FC<{ executionId: string }> = ({ executionId }) => {
  const handleExport = () => {
    // Apenas redireciona para a rota da API (baixando o arquivo). 
    // Como a API no FastAPI gerará um StreamingResponse com header de attachment, 
    // o navegador automaticamente fará o download sem sair da página.
    window.open(`http://localhost:8000/api/v1/executions/${executionId}/export`, '_blank');
  };

  return (
    <div className="flex justify-center items-center py-12">
      <GlassCard className="max-w-md w-full p-8 text-center">
        <div className="flex justify-center mb-6">
          <div className="bg-primary-100 dark:bg-primary-900/30 p-4 rounded-full">
            <FileSpreadsheet className="w-12 h-12 text-primary-600 dark:text-primary-400" />
          </div>
        </div>
        
        <h3 className="text-2xl font-bold mb-2">Lote Contábil</h3>
        <p className="text-gray-500 dark:text-gray-400 mb-8">
          Todos os lançamentos gerados a partir das conciliações aprovadas estão prontos para serem importados no seu ERP Contábil (Domínio, Questor, Fortes).
        </p>
        
        <Button 
          size="lg" 
          onClick={handleExport}
          className="w-full text-lg h-14"
          leftIcon={<Download className="w-5 h-5" />}
        >
          Baixar CSV de Lançamentos
        </Button>
      </GlassCard>
    </div>
  );
};
