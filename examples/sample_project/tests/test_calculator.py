"""Tests para Calculator."""

import pytest
from src.calculator import Calculator


class TestCalculator:
    """Tests para la clase Calculator."""

    def setup_method(self):
        """Setup para cada test."""
        self.calc = Calculator()

    def test_add(self):
        """Test suma."""
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0.5, 0.5) == 1.0

    def test_subtract(self):
        """Test resta."""
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(3, 5) == -2

    def test_multiply(self):
        """Test multiplicación."""
        assert self.calc.multiply(3, 4) == 12
        assert self.calc.multiply(-2, 3) == -6
        assert self.calc.multiply(0, 100) == 0

    def test_divide(self):
        """Test división."""
        assert self.calc.divide(10, 2) == 5
        assert self.calc.divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        """Test división por cero."""
        with pytest.raises(ValueError, match="No se puede dividir por cero"):
            self.calc.divide(10, 0)

    def test_history(self):
        """Test historial de operaciones."""
        self.calc.add(1, 2)
        self.calc.multiply(3, 4)

        assert len(self.calc.history) == 2
        assert self.calc.history == [3, 12]
        assert self.calc.last_result == 12

    def test_clear_history(self):
        """Test limpiar historial."""
        self.calc.add(1, 2)
        self.calc.clear_history()

        assert self.calc.history == []
        assert self.calc.last_result == 0
