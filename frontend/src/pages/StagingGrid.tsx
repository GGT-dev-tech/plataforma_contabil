import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, Play, Trash2, Edit3, Save, RefreshCw } from 'lucide-react';
import { apiClient as api } from '../services/api';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';

interface StagingItem {
  id: string;
  tipo: 'RECEITA' | 'DESPESA' | 'EXTRATO' | 'DINHEIRO';
  data: string;
  descricao: string;
  valor: number;
  entidade_nome?: string;
  cnpj_cpf?: string;
  categoria?: string;
  conta_origem?: string;
  conta_destino?: string;
  forma_pagamento?: string;
  processado: boolean;
}

export const StagingGrid: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [items, setItems] = useState<StagingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<StagingItem>>({});
  const [activeTab, setActiveTab] = useState<string>('ALL');

  useEffect(() => {
    fetchStagingItems();
  }, [id]);

  const fetchStagingItems = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/executions/${id}/staging`);
      setItems(res.data);
    } catch (err) {
      console.error('Erro ao buscar staging:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTemplate = () => {
    window.open(`${api.defaults.baseURL}/templates/standard`, '_blank');
  };

  const handleEdit = (item: StagingItem) => {
    setEditingId(item.id);
    setEditForm({ ...item });
  };

  const handleSave = async (itemId: string) => {
    try {
      await api.put(`/executions/${id}/staging/${itemId}`, editForm);
      setEditingId(null);
      fetchStagingItems();
    } catch (err) {
      console.error('Erro ao salvar item:', err);
    }
  };

  const handleDelete = async (itemId: string) => {
    try {
      await api.delete(`/executions/${id}/staging/${itemId}`);
      setItems(prev => prev.filter(i => i.id !== itemId));
    } catch (err) {
      console.error('Erro ao deletar item:', err);
    }
  };

  const handleProcessStaging = async () => {
    try {
      setProcessing(true);
      await api.post(`/executions/${id}/approve-staging`);
      navigate(`/executions/${id}`);
    } catch (err) {
      console.error('Erro ao processar staging:', err);
      alert('Erro ao processar registros de staging.');
    } finally {
      setProcessing(false);
    }
  };

  const filteredItems = activeTab === 'ALL' 
    ? items 
    : items.filter(i => i.tipo === activeTab);

  const getTipoBadge = (tipo: string) => {
    switch (tipo) {
      case 'RECEITA': return <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-1 rounded text-xs font-semibold">Receita</span>;
      case 'DESPESA': return <span className="bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-1 rounded text-xs font-semibold">Despesa</span>;
      case 'EXTRATO': return <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-1 rounded text-xs font-semibold">Extrato</span>;
      case 'DINHEIRO': return <span className="bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-2 py-1 rounded text-xs font-semibold">Caixa</span>;
      default: return <span className="bg-white/10 text-gray-300 border border-white/20 px-2 py-1 rounded text-xs font-semibold">{tipo}</span>;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-2 animate-fade-in">
      <Breadcrumb items={[{ label: 'Execuções', href: '/executions' }, { label: 'Revisão de Staging' }]} />

      <PageHeader 
        title="Área de Revisão Interativa" 
        description="Confira e ajuste as movimentações em massa antes de processar a conciliação final."
        action={
          <div className="flex gap-3">
            <button onClick={handleDownloadTemplate} className="glass-button flex items-center gap-2">
              <Download className="w-4 h-4" />
              <span>Baixar Modelo</span>
            </button>
            <button 
              onClick={handleProcessStaging} 
              disabled={items.length === 0 || processing}
              className="glass-button-primary flex items-center gap-2"
            >
              {processing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>Aprovar e Iniciar Conciliação</span>
            </button>
          </div>
        }
      />

      {/* Tabs Filter */}
      <div className="flex space-x-2 border-b border-white/10 pb-2">
        {['ALL', 'RECEITA', 'DESPESA', 'EXTRATO', 'DINHEIRO'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === tab 
                ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30' 
                : 'text-gray-400 hover:bg-white/5 border border-transparent'
            }`}
          >
            {tab === 'ALL' ? 'Todos' : tab}
          </button>
        ))}
      </div>

      {/* Data Table */}
      <div className="glass rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-white/5 border-b border-white/10 uppercase text-xs font-semibold tracking-wider text-gray-400">
              <tr>
                <th className="p-4">Tipo</th>
                <th className="p-4">Data</th>
                <th className="p-4">Descrição</th>
                <th className="p-4">Entidade</th>
                <th className="p-4 text-right">Valor</th>
                <th className="p-4">Conta</th>
                <th className="p-4 text-center">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-gray-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-4 text-primary-500" />
                    Carregando registros...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-gray-500">
                    <div className="text-xl mb-2">📭</div>
                    Nenhum registro encontrado.
                  </td>
                </tr>
              ) : (
                filteredItems.map(item => {
                  const isEditing = editingId === item.id;

                  return (
                    <tr key={item.id} className="hover:bg-white/5 transition-colors group">
                      <td className="p-4">{getTipoBadge(item.tipo)}</td>
                      <td className="p-4 whitespace-nowrap">
                        {isEditing ? (
                          <input 
                            type="date" 
                            value={editForm.data || ''} 
                            onChange={e => setEditForm({ ...editForm, data: e.target.value })}
                            className="glass-input p-1"
                          />
                        ) : item.data}
                      </td>
                      <td className="p-4 font-medium text-gray-200">
                        {isEditing ? (
                          <input 
                            type="text" 
                            value={editForm.descricao || ''} 
                            onChange={e => setEditForm({ ...editForm, descricao: e.target.value })}
                            className="glass-input p-1 w-full"
                          />
                        ) : item.descricao}
                      </td>
                      <td className="p-4 text-gray-400 group-hover:text-gray-300 transition-colors">
                        {isEditing ? (
                          <input 
                            type="text" 
                            value={editForm.entidade_nome || ''} 
                            onChange={e => setEditForm({ ...editForm, entidade_nome: e.target.value })}
                            className="glass-input p-1 w-full"
                          />
                        ) : (item.entidade_nome || '-')}
                      </td>
                      <td className={`p-4 text-right font-mono font-semibold whitespace-nowrap ${item.valor < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                        {isEditing ? (
                          <input 
                            type="number" 
                            step="0.01"
                            value={editForm.valor || 0} 
                            onChange={e => setEditForm({ ...editForm, valor: parseFloat(e.target.value) })}
                            className="glass-input p-1 w-24 text-right"
                          />
                        ) : `R$ ${Math.abs(item.valor).toFixed(2)}`}
                      </td>
                      <td className="p-4 text-gray-500">
                        {isEditing ? (
                          <input 
                            type="text" 
                            value={editForm.conta_origem || editForm.conta_destino || ''} 
                            onChange={e => setEditForm({ ...editForm, conta_origem: e.target.value, conta_destino: e.target.value })}
                            className="glass-input p-1 w-full"
                          />
                        ) : (item.conta_origem || item.conta_destino || '-')}
                      </td>
                      <td className="p-4 text-center">
                        {isEditing ? (
                          <button onClick={() => handleSave(item.id)} className="p-2 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 rounded-lg transition-colors">
                            <Save className="w-4 h-4" />
                          </button>
                        ) : (
                          <div className="flex justify-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onClick={() => handleEdit(item)} className="p-2 text-primary-400 bg-primary-500/10 hover:bg-primary-500/20 rounded-lg transition-colors">
                              <Edit3 className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleDelete(item.id)} className="p-2 text-red-400 bg-red-500/10 hover:bg-red-500/20 rounded-lg transition-colors">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
