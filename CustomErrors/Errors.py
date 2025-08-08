class OutOfDateError(Exception):
    """
    Licitação está fora do prazo
    """
    
    def __init__(self, message="Licitação fora do prazo", data_limite=None, data_atual=None):
        self.message = message
        self.data_limite = data_limite
        self.data_atual = data_atual
        super().__init__(self.message)
    
    def __str__(self):
        if self.data_limite and self.data_atual:
            return f"{self.message} - Data limite: {self.data_limite}, Data atual: {self.data_atual}"
        return self.message
    
class NotEditalError(Exception):
    """
    Não é edital
    """
    
    def __init__(self, message="Licitação fora do prazo", data_limite=None, data_atual=None):
        self.message = message
        self.data_limite = data_limite
        self.data_atual = data_atual
        super().__init__(self.message)
    
    def __str__(self):
        if self.data_limite and self.data_atual:
            return f"{self.message} - Data limite: {self.data_limite}, Data atual: {self.data_atual}"
        return self.message