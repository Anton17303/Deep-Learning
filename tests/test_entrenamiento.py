import os
import unittest

os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('USE_FLAX', '0')


class TestPerdidaSQL(unittest.TestCase):
    def test_logits_de_respuesta_conservan_la_perdida(self):
        import torch
        from transformers import Qwen2Config, Qwen2ForCausalLM
        torch.manual_seed(2026)
        modelo = Qwen2ForCausalLM(Qwen2Config(vocab_size=32, hidden_size=16,
            intermediate_size=32, num_hidden_layers=1, num_attention_heads=2,
            num_key_value_heads=1, max_position_embeddings=32))
        modelo.eval()
        ids = torch.tensor([[1, 7, 9, 11, 14, 3]])
        labels = torch.tensor([[-100, -100, -100, -100, 14, 3]])
        with torch.no_grad():
            completa = modelo(input_ids=ids, labels=labels).loss
            sql = modelo(input_ids=ids, labels=labels[:, -3:], logits_to_keep=3).loss
        torch.testing.assert_close(completa, sql)


if __name__ == '__main__':
    unittest.main()
