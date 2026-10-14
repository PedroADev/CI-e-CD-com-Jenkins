package integracao;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class AlunoTest {

    @Test
    void testCalcularAprovacao_ReprovacaoFrequencia() {
        Aluno aluno = new Aluno();
        aluno.setFrequencia(74);

        assertFalse(aluno.calcularAprovacao());
    }

    @Test
    void testCalcularAprovacao_ReprovacaoNota() {
        Aluno aluno = new Aluno();
        aluno.setFrequencia(75);
        aluno.setNota1(29);
        aluno.setNota2(30);

        assertFalse(aluno.calcularAprovacao());
    }

    @Test
    void testAprovacao_AprovacaoNota() {
        Aluno aluno = new Aluno();
        aluno.setFrequencia(75);
        aluno.setNota1(70);
        aluno.setNota2(70);

        assertTrue(aluno.calcularAprovacao());
    }

    @Test
    void testAprovacao_AprovacaoFinal() {
        Aluno aluno = new Aluno();
        aluno.setFrequencia(75);
        aluno.setNota1(30);
        aluno.setNota2(30);
        aluno.setNotaFinal(70);

        assertTrue(aluno.calcularAprovacao());
    }

    @Test
    void testCalcularAprovacao_ReprovacaoFinal() {
        Aluno aluno = new Aluno();
        aluno.setFrequencia(75);
        aluno.setNota1(30);
        aluno.setNota2(30);
        aluno.setNotaFinal(69);

        assertFalse(aluno.calcularAprovacao());
    }
}
