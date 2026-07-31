import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Download, Upload, Play, Trash2, Edit3, Save, Plus, 
  FileSpreadsheet, ArrowLeft, CheckCircle2, DollarSign, RefreshCw 
} from 'lucide-react';
import api from '../services/api';
import { GlassPanel } from '../components/ui/GlassPanel';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
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
      await api.post(`/executions/${id}/staging/process`);
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
      case 'RECEITA': return <Badge variant="success">Receita</Badge>;
      case 'DESPESA': return <Badge variant="danger">Despesa</Badge>;
      case 'EXTRATO': return <Badge variant="info">Extrato Bancário</Badge>;
      case 'DINHEIRO': return <Badge variant="warning">Dinheiro (Caixa)</Badge>;
      default: return <Badge variant="neutral">{tipo}</Badge>;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      <Breadcrumb items={[{ label: 'Execuções', href: '/executions' }, { label: 'Revisão e Edição Interativa' }]} />

      <PageHeader 
        title="Área de Revisão Interativa (Staging CRUD)" 
        description="Confira, edite ou adicione movimentações e contas antes de calcular a conciliação 3-Way e os impostos."
      >
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleDownloadTemplate} icon={Download}>
            Baixar Modelo Padrão .xlsx
          </Button>
          <Button 
            onClick={handleProcessStaging} 
            isLoading={processing} 
            disabled={items.length === 0 || processing}
            icon={Play}
          >
            Salvar e Calcular Conciliação
          </Button>
        </div>
      </PageHeader>

      {/* Tabs Filter */}
      <div className="flex space-x-2 border-b border-gray-200 dark:border-gray-700/50 pb-2">
        {['ALL', 'RECEITA', 'DESPESA', 'EXTRATO', 'DINHEIRO'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === tab 
                ? 'bg-primary-600 text-white shadow' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
          >
            {tab === 'ALL' ? 'Todos os Registros' : tab}
          </button>
        ))}
      </div>

      {/* Data Table */}
      <GlassPanel className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-100/50 dark:bg-gray-800/50 text-gray-700 dark:text-gray-300 font-semibold border-b border-gray-200 dark:border-gray-700/50">
              <tr>
                <th className="p-4">Tipo</th>
                <th className="p-4">Data</th>
                <th className="p-4">Descrição</th>
                <th className="p-4">Entidade / Fornecedor</th>
                <th className="p-4 text-right">Valor R$</th>
                <th className="p-4">Conta Origem/Destino</th>
                <th className="p-4 text-center">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-gray-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                    Carregando dados de staging...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-gray-500">
                    Nenhum registro encontrado nesta categoria.
                  </td>
                </tr>
              ) : (
                filteredItems.map(item => {
                  const isEditing = editingId === item.id;

                  return (
                    <tr key={item.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                      <td className="p-4">{getTipoBadge(item.tipo)}</td>
                      <td className="p-4">
                        {isEditing ? (
                          <input 
                            type="date" 
                            value={editForm.data || ''} 
                            onChange={e => setEditForm({ ...editForm, data: e.target.value })}
                            className="p-1 border rounded bg-white dark:bg-gray-800 dark:text-white"
                          />
                        ) : item.data}
                      </td>
                      <td className="p-4 font-medium text-gray-900 dark:text-gray-100">
                        {isEditing ? (
                          <input 
                            type="text" 
                            value={editForm.descricao || ''} 
                            onChange={e => setEditForm({ ...editForm, descricao: e.target.value })}
                            className="p-1 border rounded w-full bg-white dark:bg-gray-800 dark:text-white"
                          />
                        ) : item.descricao}
                      </td>
                      <td className="p-4">
                        {isEditing ? (
                          <input 
                            type="text" 
                            value={editForm.entidade_nome || ''} 
                            onChange={e => setEditForm({ ...editForm, entidade_nome: e.target.value })}
                            className="p-1 border rounded w-full bg-white dark:bg-gray-800 dark:text-white"
                          />
                        ) : (item.entidade_nome || '-')}
                      </td>
                      <td className={`p-4 text-right font-mono font-semibold ${item.valor < 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                        {isEditing ? (
                          <input 
                            type="number" 
                            step="0.01"
                            value={editForm.valor || 0} 
                            onChange={e => setEditForm({ ...editForm, valor: parseFloat(e.target.value) })}
                            className="p-1 border rounded w-28 text-right bg-white dark:bg-gray-800 dark:text-white"
                          />
                        ) : `R$ ${Math.abs(item.valor).toFixed(2)}`}
                      </td>
                      <td className="p-4 text-gray-600 dark:text-gray-400">
                        {isEditing ? (
                          <input 
                            type="text" 
                            value={editForm.conta_origem || editForm.conta_destino || ''} 
                            onChange={e => setEditForm({ ...editForm, conta_origem: e.target.value, conta_destino: e.target.value })}
                            className="p-1 border rounded w-full bg-white dark:bg-gray-800 dark:text-white"
                          />
                        ) : (item.conta_origem || item.conta_destino || '-')}
                      </td>
                      <td className="p-4 text-center">
                        {isEditing ? (
                          <button onClick={() => handleSave(item.id)} className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded">
                            <Save className="w-4 h-4" />
                          </button>
                        ) : (
                          <div className="flex justify-center space-x-2">
                            <button onClick={() => handleEdit(item)} className="p-1.5 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
                              <Edit3 className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleDelete(item.id)} className="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
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
      </GlassPanel>
    </div>
  );
};
