import axios from 'axios';
import {
  ComparisonResponse,
  ComparisonListItem,
  EvaluationMetrics,
} from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<{
    status: string;
    app: string;
    version: string;
    nlp_engine: string;
    is_fallback: boolean;
  }> {
    const res = await axios.get(`${API_BASE}/health`);
    return res.data;
  },

  async compareDocuments(formData: FormData): Promise<ComparisonResponse> {
    const res = await axios.post(`${API_BASE}/compare`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async getComparisons(): Promise<ComparisonListItem[]> {
    const res = await axios.get(`${API_BASE}/comparisons`);
    return res.data;
  },

  async getComparison(id: string): Promise<ComparisonResponse> {
    const res = await axios.get(`${API_BASE}/comparisons/${id}`);
    return res.data;
  },

  async deleteComparison(id: string): Promise<{ message: string; id: string }> {
    const res = await axios.delete(`${API_BASE}/comparisons/${id}`);
    return res.data;
  },

  async updateReviewStatus(
    changeId: string,
    isReviewed: boolean
  ): Promise<{ id: string; is_reviewed: boolean }> {
    const res = await axios.patch(`${API_BASE}/changes/${changeId}/review`, {
      is_reviewed: isReviewed,
    });
    return res.data;
  },

  async getDemoComparison(): Promise<ComparisonResponse> {
    const res = await axios.get(`${API_BASE}/demo`);
    return res.data;
  },

  async getEvaluationMetrics(): Promise<EvaluationMetrics> {
    const res = await axios.get(`${API_BASE}/evaluation`);
    return res.data;
  },

  getPdfReportUrl(comparisonId: string): string {
    return `${API_BASE}/comparisons/${comparisonId}/report/pdf`;
  },

  getCsvReportUrl(comparisonId: string): string {
    return `${API_BASE}/comparisons/${comparisonId}/report/csv`;
  },
};
