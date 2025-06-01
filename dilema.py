import pygame
import sys
import time
import math

# --- Configurações Iniciais ---
# Inicialização do Pygame
pygame.init()

# Dimensões da tela
WIDTH, HEIGHT = 900, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dilema do Prisioneiro - Torneio Caprichoso vs Garantido")

# Cores
COLORS = {
    "BACKGROUND": (240, 240, 245),
    "BLUE": (30, 80, 200),         # Caprichoso
    "RED": (200, 40, 60),          # Garantido
    "LIGHT_BLUE": (180, 200, 255),
    "LIGHT_RED": (255, 180, 180),
    "WHITE": (255, 255, 255),
    "BLACK": (30, 30, 35),
    "GRAY": (180, 180, 190),
    "GREEN": (0, 150, 70),
    "ORANGE": (200, 120, 50),
    "YELLOW": (220, 180, 0),
    "TIMER_PROGRESS": (255, 100, 100),
    "TIMER_BORDER": (200, 60, 60),
    "TIMER_BG": (220, 220, 230),
    "SCOREBOARD_BG": (230, 230, 240),
}

# Fontes
FONTS = {
    "title": pygame.font.SysFont("Arial", 40, bold=True),
    "header": pygame.font.SysFont("Arial", 32, bold=True),
    "option": pygame.font.SysFont("Arial", 28),
    "result": pygame.font.SysFont("Arial", 34, bold=True),
    "small": pygame.font.SysFont("Arial", 22),
    "score": pygame.font.SysFont("Arial", 36, bold=True),
    "timer": pygame.font.SysFont("Arial", 48, bold=True),
    "rep": pygame.font.SysFont("Arial", 24),
    "input": pygame.font.SysFont("Arial", 30),
}

# --- Estados do Jogo (Enum) ---
class GameState:
    REPRESENTATIVE = 0  # Coletar nomes dos representantes
    CHOOSING = 1        # Jogadores fazendo suas escolhas
    RESULT = 2          # Mostrar o resultado da rodada
    FINAL_RESULT = 3    # Mostrar o resultado final do torneio

# --- Classe Principal do Jogo ---
class Game:
    def __init__(self):
        self.current_state = GameState.REPRESENTATIVE
        self.cap_choice = None
        self.gar_choice = None
        self.result_text = ""
        self.result_color = COLORS["BLACK"]
        self.start_time = 0
        self.round_time = 10  # 10 segundos por rodada
        self.current_round = 1
        self.max_rounds = 20

        self.caprichoso_score = 0
        self.garantido_score = 0
        self.history = []  # Armazena o histórico de cada rodada

        # Variáveis para input de representantes
        self.cap_representative = ""
        self.gar_representative = ""
        self.cap_input_active = True
        self.gar_input_active = False

        # Retângulos dos botões e caixas de input
        self.buttons = {
            "cap_confess": pygame.Rect(100, 500, 200, 70),
            "cap_negar": pygame.Rect(100, 600, 200, 70),
            "gar_confess": pygame.Rect(600, 500, 200, 70),
            "gar_negar": pygame.Rect(600, 600, 200, 70),
            "next": pygame.Rect(350, 700, 200, 50),
            "start": pygame.Rect(350, 500, 200, 50),
            "cap_input_box": pygame.Rect(150, 340, 300, 50),
            "gar_input_box": pygame.Rect(450, 340, 300, 50),
        }

    def reset_game(self):
        """Reinicia todas as variáveis do jogo para um novo torneio."""
        self.current_state = GameState.REPRESENTATIVE
        self.cap_choice = None
        self.gar_choice = None
        self.result_text = ""
        self.result_color = COLORS["BLACK"]
        self.start_time = 0
        self.current_round = 1
        self.caprichoso_score = 0
        self.garantido_score = 0
        self.history = []
        self.cap_representative = ""
        self.gar_representative = ""
        self.cap_input_active = True
        self.gar_input_active = False

    def calculate_result(self):
        """Calcula o resultado da rodada com base nas escolhas dos jogadores."""
        if self.cap_choice == "Confessar" and self.gar_choice == "Negar":
            self.result_text = "Caprichoso: 1 ano | Garantido: 10 anos"
            self.result_color = COLORS["BLUE"]
            cap_penalty = 1
            gar_penalty = 10
        elif self.cap_choice == "Negar" and self.gar_choice == "Confessar":
            self.result_text = "Caprichoso: 10 anos | Garantido: 1 ano"
            self.result_color = COLORS["RED"]
            cap_penalty = 10
            gar_penalty = 1
        elif self.cap_choice == "Confessar" and self.gar_choice == "Confessar":
            self.result_text = "Ambos: 3 anos de prisão"
            self.result_color = COLORS["ORANGE"]
            cap_penalty = 3
            gar_penalty = 3
        else:  # Ambos negaram
            self.result_text = "Ambos: 2 anos de prisão (pena original)"
            self.result_color = COLORS["GREEN"]
            cap_penalty = 2
            gar_penalty = 2

        self.caprichoso_score += cap_penalty
        self.garantido_score += gar_penalty

        # Adicionar ao histórico
        self.history.append({
            "round": self.current_round,
            "cap_rep": self.cap_representative,
            "gar_rep": self.gar_representative,
            "cap_choice": self.cap_choice,
            "gar_choice": self.gar_choice,
            "result_text": self.result_text,
            "result_color": self.result_color, # Adicionar cor para o histórico
            "cap_penalty": cap_penalty,
            "gar_penalty": gar_penalty,
            "cap_score_total": self.caprichoso_score, # Pontuação total até o momento
            "gar_score_total": self.garantido_score
        })

    def _draw_scoreboard(self):
        """Desenha o placar atual na tela."""
        score_bg = pygame.Rect(WIDTH // 2 - 200, 20, 400, 80)
        pygame.draw.rect(SCREEN, COLORS["SCOREBOARD_BG"], score_bg, border_radius=15)
        pygame.draw.rect(SCREEN, COLORS["BLACK"], score_bg, 3, border_radius=15)

        cap_text = FONTS["option"].render("CAPRICHOSO", True, COLORS["BLUE"])
        gar_text = FONTS["option"].render("GARANTIDO", True, COLORS["RED"])
        SCREEN.blit(cap_text, (WIDTH // 2 - 150 - cap_text.get_width() // 2, 40))
        SCREEN.blit(gar_text, (WIDTH // 2 + 150 - gar_text.get_width() // 2, 40))

        cap_score = FONTS["score"].render(f"{self.caprichoso_score}", True, COLORS["BLUE"])
        gar_score = FONTS["score"].render(f"{self.garantido_score}", True, COLORS["RED"])
        SCREEN.blit(cap_score, (WIDTH // 2 - 150 - cap_score.get_width() // 2, 70))
        SCREEN.blit(gar_score, (WIDTH // 2 + 150 - gar_score.get_width() // 2, 70))

        pygame.draw.line(SCREEN, COLORS["BLACK"], (WIDTH // 2, 30), (WIDTH // 2, 90), 2)

    def _draw_timer(self, elapsed_time):
        """Desenha o círculo do temporizador e o número da rodada."""
        center_x, center_y = WIDTH // 2, 180
        radius = 40

        progress = elapsed_time / self.round_time
        angle = 2 * math.pi * progress

        pygame.draw.circle(SCREEN, COLORS["TIMER_BG"], (center_x, center_y), radius)

        if progress < 1:
            points = [(center_x, center_y)]
            for i in range(int(angle * 180 / math.pi) + 1):
                rad = i * math.pi / 180
                points.append((
                    center_x + radius * math.cos(rad - math.pi / 2),
                    center_y + radius * math.sin(rad - math.pi / 2)
                ))
            if len(points) > 2:
                pygame.draw.polygon(SCREEN, COLORS["TIMER_PROGRESS"], points)

        pygame.draw.circle(SCREEN, COLORS["TIMER_BORDER"], (center_x, center_y), radius, 3)

        time_left = max(0, self.round_time - elapsed_time)
        timer_text = FONTS["timer"].render(f"{int(time_left)}", True, COLORS["TIMER_BORDER"])
        SCREEN.blit(timer_text, (center_x - timer_text.get_width() // 2,
                                  center_y - timer_text.get_height() // 2))

        round_text = FONTS["header"].render(f"Rodada {self.current_round}/{self.max_rounds}", True, COLORS["BLACK"])
        SCREEN.blit(round_text, (center_x - round_text.get_width() // 2, center_y - 100))

    def _draw_representative_screen(self):
        """Desenha a tela para coletar os nomes dos representantes."""
        SCREEN.fill(COLORS["BACKGROUND"])

        title = FONTS["title"].render("Registrar Representantes", True, COLORS["BLACK"])
        subtitle = FONTS["header"].render(f"Rodada {self.current_round}", True, COLORS["BLACK"])
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        SCREEN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 160))

        instructions = FONTS["rep"].render("Digite o nome dos representantes para esta rodada:", True, COLORS["BLACK"])
        SCREEN.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 220))

        # Campo para Caprichoso
        cap_label = FONTS["rep"].render("Representante Caprichoso:", True, COLORS["BLUE"])
        SCREEN.blit(cap_label, (150, 300))
        
        cap_box = self.buttons["cap_input_box"]
        color_cap = COLORS["BLUE"] if self.cap_input_active else COLORS["GRAY"]
        pygame.draw.rect(SCREEN, COLORS["WHITE"], cap_box)
        pygame.draw.rect(SCREEN, color_cap, cap_box, 3)
        cap_text = FONTS["input"].render(self.cap_representative, True, COLORS["BLACK"])
        SCREEN.blit(cap_text, (cap_box.x + 10, cap_box.y + cap_box.height // 2 - cap_text.get_height() // 2))

        # Campo para Garantido
        gar_label = FONTS["rep"].render("Representante Garantido:", True, COLORS["RED"])
        SCREEN.blit(gar_label, (450, 300))
        
        gar_box = self.buttons["gar_input_box"]
        color_gar = COLORS["RED"] if self.gar_input_active else COLORS["GRAY"]
        pygame.draw.rect(SCREEN, COLORS["WHITE"], gar_box)
        pygame.draw.rect(SCREEN, color_gar, gar_box, 3)
        gar_text = FONTS["input"].render(self.gar_representative, True, COLORS["BLACK"])
        SCREEN.blit(gar_text, (gar_box.x + 10, gar_box.y + gar_box.height // 2 - gar_text.get_height() // 2))

        # Botão para iniciar a rodada
        start_button = self.buttons["start"]
        pygame.draw.rect(SCREEN, COLORS["LIGHT_BLUE"] if start_button.collidepoint(pygame.mouse.get_pos()) else COLORS["WHITE"],
                         start_button, border_radius=10)
        pygame.draw.rect(SCREEN, COLORS["GREEN"], start_button, 3, border_radius=10)
        start_text = FONTS["option"].render("Iniciar Rodada", True, COLORS["GREEN"])
        SCREEN.blit(start_text, (start_button.centerx - start_text.get_width() // 2,
                                  start_button.centery - start_text.get_height() // 2))
        
        note = FONTS["small"].render("Pressione TAB para alternar entre os campos ou clique neles", True, COLORS["GRAY"])
        SCREEN.blit(note, (WIDTH//2 - note.get_width()//2, 420))


    def _draw_main_game_screen(self, elapsed_time):
        """Desenha a tela principal do jogo (fase de escolha e resultado da rodada)."""
        SCREEN.fill(COLORS["BACKGROUND"])
        self._draw_scoreboard() # O placar é visível em CHOOSING e RESULT

        title = FONTS["title"].render("Dilema do Prisioneiro", True, COLORS["BLACK"])
        subtitle = FONTS["option"].render("Caprichoso (Azul) vs Garantido (Vermelho)", True, COLORS["BLACK"])
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        SCREEN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 170))

        if self.current_state == GameState.CHOOSING:
            self._draw_timer(elapsed_time)
        
        # Representantes atuais
        rep_bg = pygame.Rect(50, 220, 800, 60)
        pygame.draw.rect(SCREEN, COLORS["SCOREBOARD_BG"], rep_bg, border_radius=10)
        pygame.draw.rect(SCREEN, COLORS["BLACK"], rep_bg, 2, border_radius=10)
        
        cap_rep_text = FONTS["rep"].render(f"Caprichoso: {self.cap_representative}", True, COLORS["BLUE"])
        gar_rep_text = FONTS["rep"].render(f"Garantido: {self.gar_representative}", True, COLORS["RED"])
        SCREEN.blit(cap_rep_text, (WIDTH // 4 - cap_rep_text.get_width() // 2, 240))
        SCREEN.blit(gar_rep_text, (3 * WIDTH // 4 - gar_rep_text.get_width() // 2, 240))

        # Explicação das opções
        pygame.draw.rect(SCREEN, COLORS["LIGHT_BLUE"], (50, 300, 800, 150), border_radius=12)
        pygame.draw.rect(SCREEN, COLORS["BLUE"], (50, 300, 800, 150), 3, border_radius=12)

        rules = [
            "Opção 1: Se Caprichoso confessar e Garantido negar: Caprichoso 1 ano, Garantido 10 anos",
            "Opção 2: Se Caprichoso negar e Garantido confessar: Caprichoso 10 anos, Garantido 1 ano",
            "Opção 3: Se ambos confessarem: cada um fica 3 anos",
            "Opção 4: Se ambos negarem: mantêm a pena original de 2 anos"
        ]

        for i, rule in enumerate(rules):
            text = FONTS["small"].render(rule, True, COLORS["BLACK"])
            SCREEN.blit(text, (70, 320 + i * 35))

        # Botões de escolha - CAPRICHOSO
        cap_title = FONTS["header"].render("CAPRICHOSO", True, COLORS["BLUE"])
        SCREEN.blit(cap_title, (200 - cap_title.get_width() // 2, 470))

        self._draw_button(self.buttons["cap_confess"], "CONFESSAR", COLORS["BLUE"], COLORS["LIGHT_BLUE"], self.cap_choice == "Confessar")
        self._draw_button(self.buttons["cap_negar"], "NEGAR", COLORS["RED"], COLORS["LIGHT_RED"], self.cap_choice == "Negar")

        # Botões de escolha - GARANTIDO
        gar_title = FONTS["header"].render("GARANTIDO", True, COLORS["RED"])
        SCREEN.blit(gar_title, (700 - gar_title.get_width() // 2, 470))

        self._draw_button(self.buttons["gar_confess"], "CONFESSAR", COLORS["BLUE"], COLORS["LIGHT_BLUE"], self.gar_choice == "Confessar")
        self._draw_button(self.buttons["gar_negar"], "NEGAR", COLORS["RED"], COLORS["LIGHT_RED"], self.gar_choice == "Negar")

        # Mostrar resultado da rodada
        if self.current_state == GameState.RESULT:
            pygame.draw.rect(SCREEN, COLORS["SCOREBOARD_BG"], (100, 320, 700, 150), border_radius=12)
            pygame.draw.rect(SCREEN, self.result_color, (100, 320, 700, 150), 3, border_radius=12)

            result_surface = FONTS["result"].render(self.result_text, True, self.result_color)
            SCREEN.blit(result_surface, (WIDTH // 2 - result_surface.get_width() // 2, 340))

            cap_choice_text = FONTS["small"].render(f"Caprichoso escolheu: {self.cap_choice}", True, COLORS["BLUE"])
            gar_choice_text = FONTS["small"].render(f"Garantido escolheu: {self.gar_choice}", True, COLORS["RED"])
            SCREEN.blit(cap_choice_text, (WIDTH // 4 - cap_choice_text.get_width() // 2, 380))
            SCREEN.blit(gar_choice_text, (3 * WIDTH // 4 - gar_choice_text.get_width() // 2, 380))

            rep_result_text = FONTS["small"].render(f"Representantes: {self.cap_representative} (Cap) | {self.gar_representative} (Gar)", True, COLORS["BLACK"])
            SCREEN.blit(rep_result_text, (WIDTH // 2 - rep_result_text.get_width() // 2, 420))
            
            # Botão de próxima rodada
            btn_label = "Próxima Rodada" if self.current_round < self.max_rounds else "Ver Resultado Final"
            self._draw_button(self.buttons["next"], btn_label, COLORS["BLUE"], COLORS["LIGHT_BLUE"])

    def _draw_button(self, rect, text_content, text_color, hover_color, chosen=False):
        """Função auxiliar para desenhar botões."""
        mouse_pos = pygame.mouse.get_pos()
        current_color = hover_color if rect.collidepoint(mouse_pos) else COLORS["WHITE"]
        pygame.draw.rect(SCREEN, current_color, rect, border_radius=10)
        pygame.draw.rect(SCREEN, text_color, rect, 3, border_radius=10)
        
        text_surface = FONTS["option"].render(text_content, True, text_color)
        SCREEN.blit(text_surface, (rect.centerx - text_surface.get_width() // 2,
                                    rect.centery - text_surface.get_height() // 2))
        
        if chosen: # Indicador visual se a escolha foi feita
            pygame.draw.circle(SCREEN, COLORS["GREEN"], (rect.right - 15, rect.centery), 8)

    def _draw_final_result_screen(self):
        """Desenha a tela de resultado final do torneio."""
        SCREEN.fill(COLORS["BACKGROUND"])

        title = FONTS["title"].render("RESULTADO FINAL", True, COLORS["BLACK"])
        subtitle = FONTS["header"].render(f"{self.max_rounds} Rodadas Completas", True, COLORS["BLACK"])
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        SCREEN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 110))

        # Placar final
        pygame.draw.rect(SCREEN, COLORS["SCOREBOARD_BG"], (WIDTH // 2 - 250, 180, 500, 150), border_radius=15)
        pygame.draw.rect(SCREEN, COLORS["BLACK"], (WIDTH // 2 - 250, 180, 500, 150), 3, border_radius=15)

        cap_final = FONTS["header"].render(f"Caprichoso: {self.caprichoso_score} anos", True, COLORS["BLUE"])
        gar_final = FONTS["header"].render(f"Garantido: {self.garantido_score} anos", True, COLORS["RED"])
        SCREEN.blit(cap_final, (WIDTH // 2 - cap_final.get_width() // 2, 210))
        SCREEN.blit(gar_final, (WIDTH // 2 - gar_final.get_width() // 2, 260))

        # Determinar o vencedor
        if self.caprichoso_score < self.garantido_score:
            winner_text = FONTS["header"].render("CAPRICHOSO VENCEU!", True, COLORS["BLUE"])
            winner_reason = FONTS["small"].render("(Menor tempo total de prisão)", True, COLORS["BLUE"])
        elif self.garantido_score < self.caprichoso_score:
            winner_text = FONTS["header"].render("GARANTIDO VENCEU!", True, COLORS["RED"])
            winner_reason = FONTS["small"].render("(Menor tempo total de prisão)", True, COLORS["RED"])
        else:
            winner_text = FONTS["header"].render("EMPATE!", True, COLORS["GREEN"])
            winner_reason = FONTS["small"].render("(Tempos de prisão iguais)", True, COLORS["GREEN"])

        SCREEN.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 360))
        SCREEN.blit(winner_reason, (WIDTH // 2 - winner_reason.get_width() // 2, 410))

        # Histórico das rodadas
        history_title = FONTS["header"].render("Histórico das Rodadas:", True, COLORS["BLACK"])
        SCREEN.blit(history_title, (WIDTH // 2 - history_title.get_width() // 2, 460))
        
        # Desenha o histórico com rolagem simulada (ou limitado a X itens)
        history_start_y = 500
        line_height = 28 # Espaçamento entre as linhas
        max_display_lines = 10 # Limite de linhas visíveis para não sobrecarregar
        
        # Se houver mais história do que podemos mostrar, mostramos as mais recentes
        display_history = self.history[-max_display_lines:]

        for i, entry in enumerate(display_history):
            y_pos = history_start_y + i * line_height
            
            # Formato de linha para cada entrada do histórico
            history_line = (
                f"Rodada {entry['round']}: "
                f"Cap: {entry['cap_rep']} ({entry['cap_choice']}) | "
                f"Gar: {entry['gar_rep']} ({entry['gar_choice']}) | "
                f"Pena: {entry['cap_penalty']}/{entry['gar_penalty']}"
            )
            history_text = FONTS["small"].render(history_line, True, COLORS["BLACK"])
            SCREEN.blit(history_text, (50, y_pos))

        # Botão para reiniciar
        self._draw_button(self.buttons["next"], "Jogar Novamente", COLORS["BLUE"], COLORS["LIGHT_BLUE"])

    def _handle_event(self, event, mouse_pos):
        """Processa um evento Pygame."""
        if event.type == pygame.QUIT:
            return False # Sinaliza para sair do loop principal

        if event.type == pygame.KEYDOWN:
            if self.current_state == GameState.REPRESENTATIVE:
                if self.cap_input_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        self.cap_input_active = False
                        self.gar_input_active = True
                    elif event.key == pygame.K_BACKSPACE:
                        self.cap_representative = self.cap_representative[:-1]
                    else:
                        if len(self.cap_representative) < 15: # Limita o tamanho do nome
                            self.cap_representative += event.unicode
                elif self.gar_input_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        self.gar_input_active = False
                        self.cap_input_active = True # Volta para caprichoso se der enter no ultimo
                    elif event.key == pygame.K_BACKSPACE:
                        self.gar_representative = self.gar_representative[:-1]
                    else:
                        if len(self.gar_representative) < 15: # Limita o tamanho do nome
                            self.gar_representative += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_state == GameState.REPRESENTATIVE:
                # Seleção de campo de representante por clique
                if self.buttons["cap_input_box"].collidepoint(mouse_pos):
                    self.cap_input_active = True
                    self.gar_input_active = False
                elif self.buttons["gar_input_box"].collidepoint(mouse_pos):
                    self.cap_input_active = False
                    self.gar_input_active = True
                elif self.buttons["start"].collidepoint(mouse_pos):
                    # Preenche com nomes padrão se estiverem vazios
                    if not self.cap_representative.strip():
                        self.cap_representative = f"Representante Caprichoso {self.current_round}"
                    if not self.gar_representative.strip():
                        self.gar_representative = f"Representante Garantido {self.current_round}"
                    
                    self.start_time = time.time() # Inicia o timer da rodada
                    self.current_state = GameState.CHOOSING # Transiciona para a fase de escolha

            elif self.current_state == GameState.CHOOSING:
                # Escolhas de Caprichoso
                if self.buttons["cap_confess"].collidepoint(mouse_pos):
                    self.cap_choice = "Confessar"
                elif self.buttons["cap_negar"].collidepoint(mouse_pos):
                    self.cap_choice = "Negar"
                
                # Escolhas de Garantido
                if self.buttons["gar_confess"].collidepoint(mouse_pos):
                    self.gar_choice = "Confessar"
                elif self.buttons["gar_negar"].collidepoint(mouse_pos):
                    self.gar_choice = "Negar"
                
                # Se ambos escolherem, calcula o resultado e muda de estado
                if self.cap_choice is not None and self.gar_choice is not None:
                    self.calculate_result()
                    self.current_state = GameState.RESULT

            elif self.current_state == GameState.RESULT:
                if self.buttons["next"].collidepoint(mouse_pos):
                    if self.current_round < self.max_rounds:
                        self.current_round += 1
                        self.cap_choice = None
                        self.gar_choice = None
                        self.result_text = ""
                        # Resetar nomes dos representantes para a próxima rodada
                        self.cap_representative = ""
                        self.gar_representative = ""
                        self.cap_input_active = True # Ativar input para a próxima rodada
                        self.gar_input_active = False
                        self.current_state = GameState.REPRESENTATIVE # Volta para a tela de representantes
                    else:
                        self.current_state = GameState.FINAL_RESULT # Vai para o resultado final

            elif self.current_state == GameState.FINAL_RESULT:
                if self.buttons["next"].collidepoint(mouse_pos):
                    self.reset_game() # Reinicia o jogo completo

        return True # Sinaliza para continuar no loop principal

    def run(self):
        """O loop principal do jogo."""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            current_time = time.time()
            elapsed_time = 0

            # Lógica do timer, só ativa na fase de escolha
            if self.current_state == GameState.CHOOSING:
                elapsed_time = current_time - self.start_time
                if elapsed_time >= self.round_time:
                    # Atribuir escolhas padrão se o tempo acabar
                    if self.cap_choice is None:
                        self.cap_choice = "Negar"
                    if self.gar_choice is None:
                        self.gar_choice = "Negar"
                    
                    self.calculate_result()
                    self.current_state = GameState.RESULT

            # Processamento de eventos
            for event in pygame.event.get():
                running = self._handle_event(event, mouse_pos)
                if not running: # Se _handle_event retornou False (QUIT), sair
                    break
            
            if not running:
                break # Sair do loop principal

            # Desenha a tela de acordo com o estado atual do jogo
            if self.current_state == GameState.REPRESENTATIVE:
                self._draw_representative_screen()
            elif self.current_state == GameState.CHOOSING or self.current_state == GameState.RESULT:
                self._draw_main_game_screen(elapsed_time)
            elif self.current_state == GameState.FINAL_RESULT:
                self._draw_final_result_screen()

            pygame.display.flip() # Atualiza a tela

        pygame.quit()
        sys.exit()

# --- Execução do Jogo ---
if __name__ == "__main__":
    # O código dentro deste bloco só será executado quando o script for rodado diretamente.
    # É uma boa prática para garantir que o jogo só inicie se for o "main" script.
    game = Game()
    game.run()