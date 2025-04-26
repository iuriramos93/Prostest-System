/**
 * Utilitários para autenticação
 */

/**
 * Obtém o token de autenticação do localStorage
 * @returns {string|null} Token de autenticação ou null se não estiver autenticado
 */
export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * Salva o token de autenticação no localStorage
 * @param {string} token - Token de autenticação
 */
export const setAuthToken = (token) => {
  localStorage.setItem('authToken', token);
};

/**
 * Remove o token de autenticação do localStorage
 */
export const removeAuthToken = () => {
  localStorage.removeItem('authToken');
};

/**
 * Verifica se o usuário está autenticado
 * @returns {boolean} True se estiver autenticado, false caso contrário
 */
export const isAuthenticated = () => {
  const token = getAuthToken();
  return !!token;
};

/**
 * Decodifica o token JWT para obter as informações do usuário
 * @returns {Object|null} Informações do usuário ou null se não estiver autenticado
 */
export const getUserInfo = () => {
  const token = getAuthToken();
  if (!token) return null;
  
  try {
    // Decodifica o token JWT (parte do meio, após o primeiro ponto)
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Erro ao decodificar token:', error);
    return null;
  }
};