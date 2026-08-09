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
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-[#0b0f19]">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0b0f19] text-gray-900 dark:text-gray-100 p-8 relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-600/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob pointer-events-none"></div>
      <div className="absolute bottom-[-15%] right-[10%] w-[35%] h-[35%] bg-accent-500/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000 pointer-events-none"></div>
      
      <div className="max-w-6xl mx-auto relative z-10">
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
              className="glass p-6 rounded-2xl border border-white/5 cursor-pointer hover:border-primary-500/30 hover:shadow-[0_0_30px_rgba(99,102,241,0.1)] transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/10 to-accent-500/10 border border-primary-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Building2 className="w-6 h-6 text-primary-400" />
                </div>
                <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-primary-400 opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0" />
              </div>
              <h3 className="text-xl font-semibold mb-1 text-white group-hover:text-primary-300 transition-colors">{empresa.nome_fantasia}</h3>
              <p className="text-sm text-gray-400 mb-4 truncate">{empresa.razao_social}</p>
              <div className="flex items-center text-xs font-mono text-gray-500 bg-white/5 py-1 px-3 rounded-md w-fit">
                CNPJ: {empresa.cnpj}
              </div>
            </div>
          ))}
          
          {workspaces.length === 0 && (
            <div className="col-span-full text-center py-20 border-2 border-dashed border-white/10 rounded-2xl">
              <Building className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Nenhum cliente cadastrado</h3>
              <p className="text-gray-400 mb-6">Comece adicionando seu primeiro cliente ao Hub.</p>
              <Button onClick={() => setShowModal(true)} variant="outline">Adicionar Cliente</Button>
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#111827] border border-white/10 p-6 rounded-2xl w-full max-w-md shadow-2xl relative">
            <h2 className="text-xl font-bold text-white mb-6">Cadastrar Novo Cliente</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">CNPJ</label>
                <input required type="text" name="cnpj" value={formData.cnpj} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50" placeholder="00.000.000/0001-00" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Razão Social</label>
                <input required type="text" name="razao_social" value={formData.razao_social} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50" placeholder="Empresa XPTO Ltda" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Nome Fantasia</label>
                <input required type="text" name="nome_fantasia" value={formData.nome_fantasia} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50" placeholder="XPTO" />
              </div>
              
              {error && <div className="p-3 bg-red-500/10 text-red-400 rounded-lg text-sm">{error}</div>}
              
              <div className="flex justify-end gap-3 mt-8">
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
