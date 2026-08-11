import React, { useState } from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { apiClient as api } from '../services/api';
import { Upload, ChevronRight, Save, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const TemplateMapping: React.FC = () => {
  const { activeWorkspaceId } = useWorkspace();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<1 | 2>(1);
  const [headers, setHeaders] = useState<string[]>([]);
  const [signature, setSignature] = useState<string>('');
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const [mapping, setMapping] = useState<Record<string, string>>({
    'Data Vencimento': '',
    'Valor Parcela': '',
    'Descrição': '',
    'Fornecedor': '',
    'Categoria': ''
  });

  const standardFields = [
    { id: 'Data Vencimento', label: 'Data da Movimentação', required: true },
    { id: 'Valor Parcela', label: 'Valor (R$)', required: true },
    { id: 'Descrição', label: 'Descrição / Histórico', required: false },
    { id: 'Fornecedor', label: 'Cliente / Fornecedor', required: false },
    { id: 'Categoria', label: 'Categoria / Grupo', required: false }
  ];

  const handleUploadTemplate = async () => {
    if (!file || !activeWorkspaceId) return;
    setLoading(true);
    setMessage(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(`/workspaces/${activeWorkspaceId}/extract-headers`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setHeaders(response.data.headers);
      setSignature(response.data.signature);
      setStep(2);
    } catch (err: any) {
      console.error(err);
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Erro ao extrair cabeçalho do arquivo.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveMapping = async () => {
    if (!activeWorkspaceId || !signature) return;
    setLoading(true);
    setMessage(null);
    try {
      // Inverter o mapping: o backend espera { "Nome da Coluna Original": "Campo Padrao" }
      // Ex: { "Data Pgto": "Data Vencimento" }
      const payload: Record<string, string> = {};
      Object.entries(mapping).forEach(([standardField, fileHeader]) => {
        if (fileHeader) {
          payload[fileHeader] = standardField;
        }
      });

      await api.post(`/workspaces/${activeWorkspaceId}/mappings/${signature}`, payload);
      setMessage({ type: 'success', text: 'Mapeamento salvo com sucesso! Agora você pode processar arquivos com este layout.' });
      setStep(1);
      setFile(null);
    } catch (err: any) {
      console.error(err);
      setMessage({ type: 'error', text: 'Erro ao salvar mapeamento.' });
    } finally {
      setLoading(false);
    }
  };

  if (!activeWorkspaceId) {
    return <div className="text-slate-500">Selecione uma empresa para configurar o template.</div>;
  }

  return (
    <div className="space-y-6">
      {message && (
        <div className={`p-4 rounded-lg text-sm border ${message.type === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
          {message.text}
        </div>
      )}

      {step === 1 && (
        <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm animate-fade-in text-center">
          <div className="mx-auto w-16 h-16 bg-primary-50 text-primary-600 flex items-center justify-center rounded-full mb-4">
            <Upload className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">Envie um arquivo de exemplo</h2>
          <p className="text-slate-500 mb-8 max-w-md mx-auto">
            Faça upload de uma planilha (Excel ou CSV) que representa o formato padrão das suas movimentações. Nós extrairemos as colunas para você mapear.
          </p>

          <input
            type="file"
            id="template-upload"
            className="hidden"
            accept=".csv, .xlsx, .xls"
            onChange={e => setFile(e.target.files?.[0] || null)}
          />
          <label
            htmlFor="template-upload"
            className="inline-block px-6 py-3 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-primary-500 hover:bg-slate-50 transition-colors w-full max-w-md"
          >
            {file ? (
              <span className="flex items-center justify-center gap-2 text-primary-700 font-medium">
                <CheckCircle2 className="w-5 h-5" /> {file.name}
              </span>
            ) : (
              <span className="text-slate-600 font-medium">Clique para selecionar o arquivo...</span>
            )}
          </label>

          <div className="mt-8">
            <Button
              onClick={handleUploadTemplate}
              disabled={!file || loading}
              rightIcon={<ChevronRight className="w-4 h-4" />}
            >
              {loading ? 'Processando...' : 'Extrair Colunas'}
            </Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-fade-in">
          <h2 className="text-lg font-bold text-slate-800 mb-2">Vincule as Colunas</h2>
          <p className="text-slate-500 mb-6">
            Para cada campo padrão do nosso sistema, selecione qual coluna correspondente no seu arquivo.
          </p>

          <div className="space-y-4">
            {standardFields.map(field => (
              <div key={field.id} className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center p-4 bg-slate-50 rounded-lg border border-slate-100">
                <div>
                  <h4 className="font-medium text-slate-800">
                    {field.label} {field.required && <span className="text-red-500">*</span>}
                  </h4>
                  <p className="text-xs text-slate-500">Campo interno do sistema</p>
                </div>
                <div>
                  <select
                    className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:outline-none focus:border-primary-500"
                    value={mapping[field.id]}
                    onChange={(e) => setMapping(prev => ({ ...prev, [field.id]: e.target.value }))}
                  >
                    <option value="">-- Não mapear --</option>
                    {headers.map((h, i) => (
                      <option key={i} value={h}>{h}</option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center mt-8 pt-6 border-t border-slate-100">
            <Button variant="outline" onClick={() => setStep(1)}>
              Voltar
            </Button>
            <Button onClick={handleSaveMapping} disabled={loading} leftIcon={<Save className="w-4 h-4" />}>
              {loading ? 'Salvando...' : 'Salvar Mapeamento'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
