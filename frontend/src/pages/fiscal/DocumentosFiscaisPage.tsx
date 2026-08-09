import React, { useEffect, useState } from 'react';
import { FileText, Calculator, Landmark, AlertCircle } from 'lucide-react';
import { getDocumentos, DocumentoFiscal, calcularRetencoes, gerarLancamentos } from '../../services/api/documentos';

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
      await fetchDocumentos(); // Refresh the list
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

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Documentos Fiscais
          </h1>
          <p className="text-gray-400 mt-1">
            Gestão de NF-e, NFS-e e RPA com cálculo automático de retenções e contabilidade.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">
          <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          Carregando documentos...
        </div>
      ) : documentos.length === 0 ? (
        <div className="text-center py-12 glass-panel rounded-2xl border border-white/5">
          <FileText className="w-12 h-12 text-gray-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-gray-300">Nenhum documento fiscal</h3>
          <p className="text-gray-500 mt-2">Faça o upload de XMLs da SEFAZ ou NFS-e no módulo de Conciliações.</p>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl border border-white/5 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-white/5 text-gray-400 font-medium border-b border-white/10 uppercase text-[10px] tracking-wider">
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
              <tbody className="divide-y divide-white/5">
                {documentos.map((doc) => (
                  <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded flex items-center justify-center font-bold text-[10px] ${doc.tipo === 'NFE' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : doc.tipo === 'NFSE' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' : 'bg-gray-700 text-gray-300'}`}>
                          {doc.tipo}
                        </div>
                        <div>
                          <div className="font-medium text-gray-200">Nº {doc.numero || '-'}</div>
                          <div className="text-[10px] text-gray-500">{doc.data_emissao ? new Date(doc.data_emissao).toLocaleDateString('pt-BR') : '-'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-300 truncate max-w-[200px]" title={doc.emitente_nome || ''}>
                        {doc.emitente_nome || 'Desconhecido'}
                      </div>
                      <div className="text-[10px] text-gray-500">{doc.emitente_cnpj_cpf}</div>
                    </td>
                    <td className="px-6 py-4 text-right font-medium">
                      {formatCurrency(doc.valor_bruto)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {doc.total_retencoes > 0 ? (
                        <div className="text-accent-400 font-medium flex items-center justify-end gap-1">
                          <AlertCircle className="w-3 h-3" />
                          -{formatCurrency(doc.total_retencoes)}
                        </div>
                      ) : (
                        <span className="text-gray-600">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right font-bold text-gray-100">
                      {formatCurrency(doc.valor_liquido_pagar)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="px-2 py-1 bg-white/5 text-gray-300 text-[10px] rounded border border-white/10 uppercase tracking-wider">
                        {doc.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button 
                          onClick={() => handleCalcularRetencoes(doc.id)}
                          disabled={processingId === doc.id}
                          className="p-2 bg-white/5 hover:bg-primary-500/20 hover:text-primary-400 rounded-lg text-gray-400 transition-colors tooltip-trigger"
                          title="Calcular Retenções (Motor Fiscal)"
                        >
                          <Calculator className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleGerarLancamentos(doc.id)}
                          disabled={processingId === doc.id}
                          className="p-2 bg-white/5 hover:bg-accent-500/20 hover:text-accent-400 rounded-lg text-gray-400 transition-colors tooltip-trigger"
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
