import React, { useEffect, useState } from 'react';
import { FileText, Calculator, Landmark, AlertCircle, RefreshCw } from 'lucide-react';
import { getDocumentos, DocumentoFiscal, calcularRetencoes, gerarLancamentos, sincronizarDocumentos } from '../../services/api/documentos';

export const DocumentosFiscaisPage: React.FC = () => {
  const [documentos, setDocumentos] = useState<DocumentoFiscal[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    fetchDocumentos();
  }, []);

  const fetchDocumentos = async () => {
    try {
      setLoading(true);
      const data = await getDocumentos();
      setDocumentos(data);
    } catch (error) {
      console.error('Failed to fetch documentos fiscais', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCalcularRetencoes = async (id: string) => {
    try {
      setProcessingId(id);
      await calcularRetencoes(id, {
        emitente_pj: true,
        emitente_simples: false,
        retencao_iss_obrigatoria: true
      });
      await fetchDocumentos();
    } catch (error) {
      console.error('Failed to calculate retencoes', error);
      alert('Erro ao calcular retenções');
    } finally {
      setProcessingId(null);
    }
  };

  const handleGerarLancamentos = async (id: string) => {
    try {
      setProcessingId(id);
      const result = await gerarLancamentos(id);
      alert(result.mensagem);
    } catch (error) {
      console.error('Failed to generate lancamentos', error);
      alert('Erro ao gerar lançamentos contábeis');
    } finally {
      setProcessingId(null);
    }
  };

  const handleSincronizar = async () => {
    try {
      setLoading(true);
      const res = await sincronizarDocumentos("dummy-obra-id", "sienge");
      alert(`Sincronização concluída! ${res.novos_documentos_importados} novos documentos importados.`);
      await fetchDocumentos();
    } catch (error) {
      console.error('Failed to sync documentos', error);
      alert('Erro ao sincronizar Documentos com o ERP Sienge. Certifique-se de sincronizar as Obras primeiro.');
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <FileText className="w-8 h-8 text-primary-600" />
            Documentos Fiscais
          </h1>
          <p className="text-slate-500 mt-1">
            Gestão de NF-e, NFS-e e RPA com cálculo automático de retenções e contabilidade.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={handleSincronizar}
            className="px-4 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg font-medium text-sm transition-colors flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            Sincronizar Notas ERP
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500 flex flex-col items-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full mb-3"></div>
          Carregando documentos...
        </div>
      ) : documentos.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200 shadow-sm p-8">
          <FileText className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-700 mb-1">Nenhum documento fiscal registrado</h3>
          <p className="text-slate-500 text-sm">Sincronize com o ERP ou envie planilhas no módulo de Upload.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase text-xs tracking-wider">
                <tr>
                  <th className="px-6 py-4">Documento</th>
                  <th className="px-6 py-4">Emitente</th>
                  <th className="px-6 py-4 text-right">Valor Bruto</th>
                  <th className="px-6 py-4 text-right">Retenções (ISS/INSS/IR)</th>
                  <th className="px-6 py-4 text-right">Valor Líquido</th>
                  <th className="px-6 py-4 text-center">Status</th>
                  <th className="px-6 py-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documentos.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded flex items-center justify-center font-bold text-xs ${doc.tipo === 'NFE' ? 'bg-blue-50 text-blue-700 border border-blue-200' : doc.tipo === 'NFSE' ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-slate-100 text-slate-700'}`}>
                          {doc.tipo}
                        </div>
                        <div>
                          <div className="font-bold text-slate-800">Nº {doc.numero || '-'}</div>
                          <div className="text-xs text-slate-500">{doc.data_emissao ? new Date(doc.data_emissao).toLocaleDateString('pt-BR') : '-'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-800 truncate max-w-[200px]" title={doc.emitente_nome || ''}>
                        {doc.emitente_nome || 'Desconhecido'}
                      </div>
                      <div className="text-xs text-slate-500">{doc.emitente_cnpj_cpf}</div>
                    </td>
                    <td className="px-6 py-4 text-right font-semibold text-slate-800">
                      {formatCurrency(doc.valor_bruto)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {doc.total_retencoes > 0 ? (
                        <div className="text-amber-600 font-semibold flex items-center justify-end gap-1">
                          <AlertCircle className="w-3.5 h-3.5" />
                          -{formatCurrency(doc.total_retencoes)}
                        </div>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right font-bold text-slate-900">
                      {formatCurrency(doc.valor_liquido_pagar)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded border border-slate-200 uppercase">
                        {doc.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button 
                          onClick={() => handleCalcularRetencoes(doc.id)}
                          disabled={processingId === doc.id}
                          className="p-1.5 bg-slate-100 hover:bg-primary-50 hover:text-primary-700 rounded-md border border-slate-200 text-slate-600 transition-colors"
                          title="Calcular Retenções (Motor Fiscal)"
                        >
                          <Calculator className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleGerarLancamentos(doc.id)}
                          disabled={processingId === doc.id}
                          className="p-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 rounded-md border border-slate-200 text-slate-600 transition-colors"
                          title="Gerar Lançamentos Contábeis (Partida Dobrada)"
                        >
                          <Landmark className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
