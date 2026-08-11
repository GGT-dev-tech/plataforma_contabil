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
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const disposition = response.headers.get('Content-Disposition');
      let filename = `exportacao_${formato}.txt`;
      if (disposition && disposition.indexOf('filename=') !== -1) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
        if (matches != null && matches[1]) { 
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
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
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Download className="w-8 h-8 text-primary-600" />
            Exportação Contábil & SPED
          </h1>
          <p className="text-slate-500 mt-1">
            Geração de arquivos magnéticos (SPED ECD) e integração com sistemas (Domínio, Questor, Fortes).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <form onSubmit={handleExport} className="space-y-6">
            <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4">
              Parâmetros da Exportação
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary-600" />
                  Formato de Saída
                </label>
                <select 
                  value={formato}
                  onChange={(e) => setFormato(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-800 focus:ring-2 focus:ring-primary-500 outline-none text-sm font-medium"
                  required
                >
                  <option value="dominio_sistemas">Domínio Sistemas (Lançamentos TXT)</option>
                  <option value="sped_ecd">SPED Contábil ECD (Leiaute 9)</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Settings className="w-4 h-4 text-slate-500" />
                  Workspace Selecionado
                </label>
                <input 
                  type="text"
                  readOnly
                  value={activeWorkspace?.razao_social || 'Nenhuma selecionada'}
                  className="w-full bg-slate-100 border border-slate-200 rounded-lg px-4 py-2.5 text-slate-600 cursor-not-allowed text-sm font-medium"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Data Inicial</label>
                <input 
                  type="date"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-800 focus:ring-2 focus:ring-primary-500 outline-none text-sm"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Data Final</label>
                <input 
                  type="date"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-800 focus:ring-2 focus:ring-primary-500 outline-none text-sm"
                  required
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button 
                type="submit"
                disabled={loading || !activeWorkspace}
                className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold text-sm shadow-sm transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                ) : (
                  <Download className="w-4 h-4" />
                )}
                Gerar Arquivo
              </button>
            </div>
          </form>
        </div>
        
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-primary-600" />
              Instruções de Importação
            </h3>
            
            {formato === 'dominio_sistemas' ? (
              <div className="text-sm text-slate-600 space-y-3">
                <p>Para importar este arquivo na Domínio Sistemas:</p>
                <ol className="list-decimal pl-4 space-y-2 text-slate-700">
                  <li>Acesse o menu <strong>Utilitários &gt; Importação &gt; Padrão</strong></li>
                  <li>Selecione o arquivo TXT baixado</li>
                  <li>Marque a opção "Lançamentos Contábeis com múltiplas partidas"</li>
                  <li>Clique em <strong>Importar</strong></li>
                </ol>
              </div>
            ) : (
              <div className="text-sm text-slate-600 space-y-3">
                <p>Para validar e transmitir o SPED ECD:</p>
                <ol className="list-decimal pl-4 space-y-2 text-slate-700">
                  <li>Abra o <strong>PVA (Programa Validador e Assinador)</strong> do SPED Contábil</li>
                  <li>Vá em <strong>Escrituração &gt; Importar</strong></li>
                  <li>Selecione o arquivo baixado (.txt)</li>
                  <li>O PVA validará os blocos O (Abertura) e I (Lançamentos Diários).</li>
                </ol>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
