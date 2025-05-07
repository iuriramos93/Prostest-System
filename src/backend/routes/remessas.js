// Rotas para gerenciamento de remessas e desistências
import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import pkg from 'pg';
import xml2js from 'xml2js';

const { Pool } = pkg;
const router = express.Router();

// Configuração do banco de dados
const pool = new Pool({
  user: 'protest_app',
  host: '127.0.0.1',
  database: 'protest_system',
  password: 'senha_segura',
  port: 5432,
});

// Configuração do multer para upload de arquivos
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = path.join(__dirname, '../../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: function (req, file, cb) {
    // Aceitar apenas arquivos XML
    if (path.extname(file.originalname).toLowerCase() !== '.xml') {
      return cb(new Error('Apenas arquivos XML são permitidos'));
    }
    cb(null, true);
  }
});

// Rota para enviar uma nova remessa
router.post('/', upload.single('arquivo'), async (req, res) => {
  const { tipo, uf, descricao } = req.body;
  const arquivo = req.file;
  const usuarioId = req.user?.id || 1; // Obter do token de autenticação

  if (!arquivo || !tipo || !uf) {
    return res.status(400).json({ message: 'Arquivo, tipo e UF são obrigatórios' });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // Inserir a remessa no banco de dados
    const remessaQuery = `
      INSERT INTO remessas (nome_arquivo, status, uf, tipo, usuario_id)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING id
    `;
    const remessaValues = [arquivo.filename, 'Pendente', uf, tipo, usuarioId];
    const remessaResult = await client.query(remessaQuery, remessaValues);
    const remessaId = remessaResult.rows[0].id;

    // Se houver descrição, atualizar o registro
    if (descricao) {
      await client.query(
        'UPDATE remessas SET descricao = $1 WHERE id = $2',
        [descricao, remessaId]
      );
    }

    // Processar o arquivo XML (exemplo simplificado)
    const xmlContent = fs.readFileSync(arquivo.path, 'utf8');
    const parser = new xml2js.Parser({ explicitArray: false });
    parser.parseString(xmlContent, async (err, result) => {
      if (err) {
        throw new Error('Erro ao processar arquivo XML');
      }

      // Aqui você processaria o conteúdo do XML e salvaria os títulos
      // Este é apenas um exemplo simplificado
      
      // Atualizar status da remessa
      await client.query(
        'UPDATE remessas SET status = $1, data_processamento = NOW() WHERE id = $2',
        ['Processado', remessaId]
      );
    });

    await client.query('COMMIT');
    res.status(201).json({ 
      message: 'Remessa enviada com sucesso', 
      id: remessaId 
    });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Erro ao processar remessa:', error);
    res.status(500).json({ message: 'Erro ao processar remessa: ' + error.message });
  } finally {
    client.release();
  }
});

// Rota para enviar uma nova desistência
router.post('/desistencias', upload.single('arquivo'), async (req, res) => {
  const { tipo, uf, descricao } = req.body;
  const arquivo = req.file;
  const usuarioId = req.user?.id || 1; // Obter do token de autenticação

  if (!arquivo || !tipo || !uf) {
    return res.status(400).json({ message: 'Arquivo, tipo e UF são obrigatórios' });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // Inserir a desistência como um tipo especial de remessa
    const remessaQuery = `
      INSERT INTO remessas (nome_arquivo, status, uf, tipo, usuario_id)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING id
    `;
    const remessaValues = [arquivo.filename, 'Pendente', uf, 'desistencia', usuarioId];
    const remessaResult = await client.query(remessaQuery, remessaValues);
    const remessaId = remessaResult.rows[0].id;

    // Se houver descrição, atualizar o registro
    if (descricao) {
      await client.query(
        'UPDATE remessas SET descricao = $1 WHERE id = $2',
        [descricao, remessaId]
      );
    }

    // Processar o arquivo XML de desistência
    // Implementação específica para desistências...

    await client.query('COMMIT');
    res.status(201).json({ 
      message: 'Desistência enviada com sucesso', 
      id: remessaId 
    });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Erro ao processar desistência:', error);
    res.status(500).json({ message: 'Erro ao processar desistência: ' + error.message });
  } finally {
    client.release();
  }
});

// Rota para listar remessas
router.get('/', async (req, res) => {
  try {
    const { tipo, uf, status, dataInicio, dataFim } = req.query;
    
    let query = 'SELECT * FROM remessas WHERE 1=1';
    const values = [];
    let paramCount = 1;
    
    if (tipo) {
      query += ` AND tipo = $${paramCount}`;
      values.push(tipo);
      paramCount++;
    }
    
    if (uf) {
      query += ` AND uf = $${paramCount}`;
      values.push(uf);
      paramCount++;
    }
    
    if (status) {
      query += ` AND status = $${paramCount}`;
      values.push(status);
      paramCount++;
    }
    
    if (dataInicio) {
      query += ` AND data_envio >= $${paramCount}`;
      values.push(dataInicio);
      paramCount++;
    }
    
    if (dataFim) {
      query += ` AND data_envio <= $${paramCount}`;
      values.push(dataFim);
      paramCount++;
    }
    
    query += ' ORDER BY data_envio DESC';
    
    const result = await pool.query(query, values);
    res.json(result.rows);
  } catch (error) {
    console.error('Erro ao listar remessas:', error);
    res.status(500).json({ message: 'Erro ao listar remessas' });
  }
});

// Rota para obter detalhes de uma remessa
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Obter detalhes da remessa
    const remessaQuery = 'SELECT * FROM remessas WHERE id = $1';
    const remessaResult = await pool.query(remessaQuery, [id]);
    
    if (remessaResult.rows.length === 0) {
      return res.status(404).json({ message: 'Remessa não encontrada' });
    }
    
    const remessa = remessaResult.rows[0];
    
    // Obter títulos associados à remessa
    const titulosQuery = 'SELECT * FROM titulos WHERE remessa_id = $1';
    const titulosResult = await pool.query(titulosQuery, [id]);
    
    res.json({
      ...remessa,
      titulos: titulosResult.rows
    });
  } catch (error) {
    console.error(`Erro ao obter remessa ${req.params.id}:`, error);
    res.status(500).json({ message: 'Erro ao obter detalhes da remessa' });
  }
});

// Exportar o router
export default router;