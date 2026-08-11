import React, { useState, useEffect } from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { apiClient as api } from '../services/api';
import { Save, Building2, Plug, Plus } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { TemplateMapping } from './TemplateMapping';

export const WorkspaceSettings: React.FC = () => {
  const { activeWorkspace, activeWorkspaceId, workspaces } = useWorkspace();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'geral' | 'integracoes' | 'ingestao'>('geral');

  // Estado para Criar Nova Empresa
  const [newCompany, setNewCompany] = useState({ cnpj: '', razao_social: '', nome_fantasia: '' });
  const [isCreating, setIsCreating] = useState(false);

  // Estado para Integrações ERP
  const [erpConfig, setErpConfig] = useState({
    provedor: 'nenhum', // 'sienge', 'contaazul', 'omie'
    api_key: '',
    tenant_id: ''
  });

  useEffect(() => {
    if (activeWorkspace?.import_config) {
      if (activeWorkspace.import_config.ERP) {
        setErpConfig(activeWorkspace.import_config.ERP);
      }
    }
  }, [activeWorkspace]);



  const handleErpChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setErpConfig(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateCompany = async () => {
    setLoading(true);
    setMessage(null);
    try {
      await api.post(`/workspaces/empresas`, newCompany);
      setMessage({ type: 'success', text: 'Empresa cadastrada com sucesso!' });
      setIsCreating(false);
      setNewCompany({ cnpj: '', razao_social: '', nome_fantasia: '' });
      setTimeout(() => window.location.reload(), 1500);
    } catch (err: any) {
      console.error(err);
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Erro ao cadastrar empresa.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfigs = async () => {
    if (!activeWorkspaceId) return;
    setLoading(true);
    setMessage(null);
    try {
      const payload = {
        ...(activeWorkspace?.import_config || {}),
        ERP: erpConfig
      };
      await api.put(`/workspaces/empresas/${activeWorkspaceId}/import-config`, payload);
      setMessage({ type: 'success', text: 'Configurações atualizadas com sucesso!' });
      setTimeout(() => window.location.reload(), 1500);
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: 'Erro ao salvar configurações.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            Gestão da Contabilidade
          </h1>
          <p className="text-slate-500">
            Administre seus clientes (empresas), parametrize conectores ERP e ajuste templates de planilhas.
          </p>
        </div>
      </div>

      <div className="flex space-x-1 bg-slate-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('geral')}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'geral' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'}`}
        >
          Meus Clientes
        </button>
        <button
          onClick={() => setActiveTab('integracoes')}
          disabled={!activeWorkspaceId}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'integracoes' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'} disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          Integrações (ERP)
        </button>
        <button
          onClick={() => setActiveTab('ingestao')}
          disabled={!activeWorkspaceId}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'ingestao' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'} disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          Templates de Planilha
        </button>
      </div>

      {message && (
        <div className={`p-4 rounded-lg text-sm border ${message.type === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
          {message.text}
        </div>
      )}

      {/* TAB GERAL: Lista de Clientes e Cadastro */}
      {activeTab === 'geral' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-primary-600" />
                Empresas Atendidas
              </h2>
              <Button onClick={() => setIsCreating(!isCreating)} variant="default" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                Novo Cliente
              </Button>
            </div>

            {isCreating && (
              <div className="mb-8 p-6 bg-slate-50 border border-slate-200 rounded-lg">
                <h3 className="text-md font-medium text-slate-800 mb-4">Cadastrar Nova Empresa</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">CNPJ</label>
                    <input type="text" value={newCompany.cnpj} onChange={e => setNewCompany({...newCompany, cnpj: e.target.value})} className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500" placeholder="00.000.000/0000-00" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Razão Social</label>
                    <input type="text" value={newCompany.razao_social} onChange={e => setNewCompany({...newCompany, razao_social: e.target.value})} className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500" placeholder="Empresa Ltda" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Nome Fantasia</label>
                    <input type="text" value={newCompany.nome_fantasia} onChange={e => setNewCompany({...newCompany, nome_fantasia: e.target.value})} className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500" placeholder="Empresa" />
                  </div>
                </div>
                <div className="flex justify-end gap-3">
                  <Button variant="outline" size="sm" onClick={() => setIsCreating(false)}>Cancelar</Button>
                  <Button variant="default" size="sm" onClick={handleCreateCompany} disabled={loading}>{loading ? 'Salvando...' : 'Salvar Empresa'}</Button>
                </div>
              </div>
            )}

            <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
              {workspaces.map(ws => (
                <div key={ws.id} className={`p-4 flex items-center justify-between ${ws.id === activeWorkspaceId ? 'bg-primary-50' : 'bg-white hover:bg-slate-50'}`}>
                  <div>
                    <p className="font-medium text-slate-900">{ws.nome_fantasia || ws.razao_social}</p>
                    <p className="text-sm text-slate-500">CNPJ: {ws.cnpj || 'Não informado'}</p>
                  </div>
                  {ws.id === activeWorkspaceId && (
                    <span className="px-2.5 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-full border border-primary-200">
                      Selecionada
                    </span>
                  )}
                </div>
              ))}
              {workspaces.length === 0 && (
                <div className="p-8 text-center text-slate-500">Nenhum cliente cadastrado.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB INTEGRACOES */}
      {activeTab === 'integracoes' && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-fade-in">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center border border-indigo-100">
              <Plug className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-800">Conectores ERP</h2>
              <p className="text-sm text-slate-500">Configure a sincronização com o software do cliente.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Sistema ERP</label>
              <select name="provedor" value={erpConfig.provedor} onChange={handleErpChange} className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500">
                <option value="nenhum">Nenhum (Upload Manual de Arquivos)</option>
                <option value="sienge">Sienge Plataforma</option>
                <option value="contaazul">ContaAzul</option>
                <option value="omie">Omie ERP</option>
              </select>
            </div>
            
            {erpConfig.provedor !== 'nenhum' && (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Tenant ID / Subdomínio</label>
                  <input type="text" name="tenant_id" value={erpConfig.tenant_id} onChange={handleErpChange} className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500" placeholder="ex: construtorax" />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-slate-700">API Key / Token de Acesso</label>
                  <input type="password" name="api_key" value={erpConfig.api_key} onChange={handleErpChange} className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500" placeholder="••••••••••••••••••••" />
                </div>
              </>
            )}
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-100">
            <Button onClick={handleSaveConfigs} disabled={loading} leftIcon={<Save className="w-4 h-4" />}>
              {loading ? 'Salvando...' : 'Salvar Conexão'}
            </Button>
          </div>
        </div>
      )}

      {/* TAB INGESTAO */}
      {activeTab === 'ingestao' && (
        <TemplateMapping />
      )}
    </div>
  );
};
