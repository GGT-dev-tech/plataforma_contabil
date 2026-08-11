import React, { useState } from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { useNavigate } from 'react-router-dom';
import { Building2, Plus, ArrowRight, Save, Building } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { apiClient } from '../services/api';

export const DashboardClientes: React.FC = () => {
  const { workspaces, setActiveWorkspaceId, isLoading, refreshWorkspaces } = useWorkspace();
  const navigate = useNavigate();
  
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    cnpj: '',
    razao_social: '',
    nome_fantasia: ''
  });

  const handleSelectClient = (id: string) => {
    setActiveWorkspaceId(id);
    navigate('/executions');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiClient.post('/workspaces/empresas', formData);
      await refreshWorkspaces();
      setShowModal(false);
      setFormData({ cnpj: '', razao_social: '', nome_fantasia: '' });
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Erro ao criar cliente.');
    } finally {
      setLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex items-center justify-between mb-12">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Hub de Clientes</h1>
            <p className="text-gray-400">Selecione uma empresa para acessar as ferramentas de conciliação.</p>
          </div>
          <Button onClick={() => setShowModal(true)} variant="default" leftIcon={<Plus className="w-4 h-4" />}>
            Novo Cliente
          </Button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workspaces.map(empresa => (
            <div 
              key={empresa.id}
              onClick={() => handleSelectClient(empresa.id)}
              className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm cursor-pointer hover:border-primary-500 hover:shadow-md transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary-50 flex items-center justify-center group-hover:bg-primary-100 transition-colors">
                  <Building2 className="w-6 h-6 text-primary-600" />
                </div>
                <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-primary-600 opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0" />
              </div>
              <h3 className="text-xl font-bold mb-1 text-slate-800">{empresa.nome_fantasia}</h3>
              <p className="text-sm text-slate-500 mb-4 truncate">{empresa.razao_social}</p>
              <div className="flex items-center text-xs font-mono text-slate-600 bg-slate-100 py-1.5 px-3 rounded-md w-fit font-medium">
                CNPJ: {empresa.cnpj}
              </div>
            </div>
          ))}
          
          {workspaces.length === 0 && (
            <div className="col-span-full text-center py-20 border-2 border-dashed border-slate-300 rounded-xl bg-white">
              <Building className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-slate-700 mb-2">Nenhum cliente cadastrado</h3>
              <p className="text-slate-500 mb-6">Comece adicionando seu primeiro cliente ao Hub.</p>
              <Button onClick={() => setShowModal(true)} variant="outline">Adicionar Cliente</Button>
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white border border-slate-200 p-6 rounded-xl w-full max-w-md shadow-xl relative">
            <h2 className="text-xl font-bold text-slate-800 mb-6">Cadastrar Novo Cliente</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">CNPJ</label>
                <input required type="text" name="cnpj" value={formData.cnpj} onChange={handleChange} className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500" placeholder="00.000.000/0001-00" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Razão Social</label>
                <input required type="text" name="razao_social" value={formData.razao_social} onChange={handleChange} className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500" placeholder="Empresa XPTO Ltda" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Nome Fantasia</label>
                <input required type="text" name="nome_fantasia" value={formData.nome_fantasia} onChange={handleChange} className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500" placeholder="XPTO" />
              </div>
              
              {error && <div className="p-3 bg-red-50 text-red-600 border border-red-100 rounded-lg text-sm">{error}</div>}
              
              <div className="flex justify-end gap-3 mt-8 pt-4 border-t border-slate-100">
                <Button type="button" variant="ghost" onClick={() => setShowModal(false)}>Cancelar</Button>
                <Button type="submit" variant="default" disabled={loading} leftIcon={<Save className="w-4 h-4" />}>
                  {loading ? 'Salvando...' : 'Salvar Cliente'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
