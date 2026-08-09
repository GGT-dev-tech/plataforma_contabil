import React, { useState } from 'react';
import { Download, FileText, Settings, AlertCircle } from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

export const ExportacaoContabilPage: React.FC = () => {
  const { activeWorkspace } = useWorkspace();
  const [loading, setLoading] = useState(false);
  const [formato, setFormato] = useState('dominio_sistemas');
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) {
      alert("Selecione um Workspace/Construtora");
      return;
    }
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const params = new URLSearchParams();
      params.append('formato', formato);
      params.append('empresa_id', activeWorkspace.id);
      
      if (dataInicio) params.append('data_inicio', dataInicio);
      if (dataFim) params.append('data_fim', dataFim);
      
      const response = await fetch(`/api/v1/exportacao/lancamentos?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao gerar exportação');
      }
      
      // Criar URL para o Blob
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      // Extrair o nome do arquivo do header (se existir)
      const disposition = response.headers.get('Content-Disposition');
      let filename = `exportacao_${formato}.txt`;
      if (disposition && disposition.indexOf('filename=') !== -1) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
        if (matches != null && matches[1]) { 
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
      // Trigger Download
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Exportação Contábil
          </h1>
          <p className="text-gray-400 mt-1">
            Geração de arquivos magnéticos (SPED) e integração com Sistemas Contábeis.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 glass-panel rounded-2xl border border-white/5 p-6">
          <form onSubmit={handleExport} className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-200 border-b border-white/5 pb-4">
              Parâmetros da Exportação
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary-400" />
                  Formato de Saída
                </label>
                <select 
                  value={formato}
                  onChange={(e) => setFormato(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all appearance-none"
                  required
                >
                  <option value="dominio_sistemas">Domínio Sistemas (Lançamentos TXT)</option>
                  <option value="sped_ecd">SPED Contábil ECD (Leiaute 9)</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <Settings className="w-4 h-4 text-accent-400" />
                  Workspace / Construtora
                </label>
                <input 
                  type="text"
                  readOnly
                  value={activeWorkspace?.razao_social || 'Nenhuma selecionada'}
                  className="w-full bg-black/20 border border-white/5 rounded-xl px-4 py-3 text-gray-400 cursor-not-allowed outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">Data Inicial</label>
                <input 
                  type="date"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">Data Final</label>
                <input 
                  type="date"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                  required
                />
              </div>
            </div>

            <div className="pt-4 border-t border-white/5 flex justify-end">
              <button 
                type="submit"
                disabled={loading || !activeWorkspace}
                className="px-6 py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] hover:shadow-[0_0_25px_rgba(37,99,235,0.3)] flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin w-5 h-5 border-2 border-white/20 border-t-white rounded-full"></div>
                ) : (
                  <Download className="w-5 h-5" />
                )}
                Gerar Arquivo
              </button>
            </div>
          </form>
        </div>
        
        <div className="space-y-4">
          <div className="glass-panel rounded-2xl border border-white/5 p-6 bg-gradient-to-br from-blue-500/5 to-purple-500/5">
            <h3 className="text-lg font-semibold text-gray-200 mb-2 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-blue-400" />
              Instruções de Importação
            </h3>
            
            {formato === 'dominio_sistemas' ? (
              <div className="text-sm text-gray-400 space-y-3">
                <p>Para importar este arquivo na Domínio Sistemas:</p>
                <ol className="list-decimal pl-4 space-y-2">
                  <li>Acesse o menu <strong>Utilitários &gt; Importação &gt; Padrão</strong></li>
                  <li>Selecione o arquivo TXT baixado</li>
                  <li>Marque a opção "Lançamentos Contábeis com múltiplas partidas"</li>
                  <li>Clique em <strong>Importar</strong></li>
                </ol>
              </div>
            ) : (
              <div className="text-sm text-gray-400 space-y-3">
                <p>Para validar e transmitir o SPED ECD:</p>
                <ol className="list-decimal pl-4 space-y-2">
                  <li>Abra o <strong>PVA (Programa Validador e Assinador)</strong> do SPED Contábil</li>
                  <li>Vá em <strong>Escrituração &gt; Importar</strong></li>
                  <li>Selecione o arquivo baixado (.txt)</li>
                  <li>O PVA validará os blocos O (Abertura) e I (Lançamentos Diários). Complete os saldos se necessário antes de assinar.</li>
                </ol>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
