import '@testing-library/jest-dom';
import 'jest-environment-jsdom';

// Mock do localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn((index: number) => null),
} as Storage;

global.localStorage = localStorageMock;

// Limpar todos os mocks após cada teste
afterEach(() => {
  jest.clearAllMocks();
});