import { Router } from 'express';
import { Erro } from '../models/erro';
import { authMiddleware } from '../middlewares/auth';

const router = Router();

router.get('/', authMiddleware, async (req, res) => {
  try {
    const { codigo, status, dataInicio, dataFim } = req.query;
    
    const filtros: any = {};
    if (codigo) filtros.codigo = codigo;
    if (status) filtros.status = status;
    if (dataInicio && dataFim) {
      filtros.dataOcorrencia = {
        $gte: new Date(dataInicio as string),
        $lte: new Date(dataFim as string)
      };
    }

    const erros = await Erro.find(filtros)
      .sort({ dataOcorrencia: -1 })
      .lean();

    res.json(erros);
  } catch (error) {
    console.error('Erro ao listar erros:', error);
    res.status(500).json({ mensagem: 'Erro interno do servidor' });
  }
});

router.put('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { solucao } = req.body;

    const erroAtualizado = await Erro.findByIdAndUpdate(
      id,
      { status: 'Resolvido', solucao, dataResolucao: new Date() },
      { new: true }
    );

    if (!erroAtualizado) {
      return res.status(404).json({ mensagem: 'Erro não encontrado' });
    }

    res.json(erroAtualizado);
  } catch (error) {
    console.error('Erro ao resolver erro:', error);
    res.status(500).json({ mensagem: 'Erro interno do servidor' });
  }
});

export default router;