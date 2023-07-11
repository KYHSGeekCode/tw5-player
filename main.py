import json
from time import sleep

import pygame


class GameWindowSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pygame.init()
        self.window_width = 800
        self.window_height = 600
        self.game_window = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.HWSURFACE | pygame.HWACCEL
        )
        self.clock = pygame.time.Clock()
        self.num_lanes = 5
        self.lane_width = self.window_width // self.num_lanes


# Step 3: Create the game objects
class Note:
    def __init__(self, note_data):
        self.start_line = note_data["StartLine"]  # Start line of the note (TODO)
        self.time = note_data["Time"]  # when should this note be at the judgement line
        self.color = note_data["Color"]
        self.end_line = note_data["EndLine"]  # actual final line of the note
        self.flick = note_data["Flick"]
        self.note_id = note_data["ID"]
        self.mode = note_data["Mode"]
        self.prev_ids = note_data["PrevIDs"]  # Long, Slide, Flick (TODO)
        self.size = note_data["Size"]
        self.speed = note_data["Speed"]
        self.position = self.start_line
        self.next_ids = []

    def get_pos_based_on_time(self, time, game):
        end_line_x = (
            self.end_line - 1
        ) * game.lane_width + game.lane_width // 2  # Adjust the position based on the lane
        start_line_x = (self.start_line - 1) * game.lane_width + game.lane_width // 2
        x = (end_line_x - start_line_x) * (
            time - self.time
        ) + end_line_x  # / (self.time - 0.0)
        y = (game.window_height - 0.0) * (
            time - self.time
        ) + game.window_height  # / (self.time - 0.0)
        return x, y

    def draw(self, game, time):
        # Implement the drawing logic for the note circle
        # draw the circle based on the current time and the note's time
        # interpolate the position of the note based on the current time and the note's time
        # draw the circle at the interpolated position

        pos = self.position
        if self.is_visible(time):
            # at t0: (x = start_line, y = 0)
            # at t1 (time): (x = end_line, y = window_height)
            # at t: (x = ?, y = ?)
            x, y = self.get_pos_based_on_time(time, game)
            if self.flick == 0:
                color = (255, 0, 0)
                if any(element != 0 for element in self.prev_ids) or any(
                    element != 0 for element in self.next_ids
                ):
                    color = (255, 255, 0)
                if self.mode == 2:  # slide note
                    color = (128, 0, 128)
                pygame.draw.circle(
                    game.game_window, color, (x, y), 10
                )  # self.color, size
            elif self.flick == 1:
                arrow_width = 60  # Width of the arrow
                arrow_height = 30  # Height of the arrow
                pygame.draw.polygon(
                    game.game_window,
                    (0, 0, 255),
                    [
                        (x, y),
                        (x, y - arrow_height // 2),
                        (x - arrow_height, y),
                        (x, y + arrow_height // 2),
                    ],
                )
            elif self.flick == 2:
                arrow_width = 60  # Width of the arrow
                arrow_height = 30  # Height of the arrow
                pygame.draw.polygon(
                    game.game_window,
                    (0, 0, 255),
                    [
                        (x, y),
                        (x, y + arrow_height // 2),
                        (x + arrow_height, y),
                        (x, y - arrow_height // 2),
                    ],
                )
        else:
            pass

    def is_visible(self, time) -> bool:
        if time > self.time + 30:
            return False
        if time < self.time - 30:
            return False
        return True


class JudgementCircle:
    def __init__(self, position):
        self.position = position

    def draw(self, game):
        game_window = game.game_window
        window_height = game.window_height
        pygame.draw.circle(
            game_window, (255, 255, 255), (self.position, window_height), 10
        )


def main():
    # Step 1: Set up the Pygame environment
    game = GameWindowSingleton()

    # Step 2: Load and parse the JSON file
    with open("sheets/2013___凸凹スピードスター___MasterPlus") as file:
        data = json.load(file)

    num_lanes = 5  # data['metadata']['level']
    artist = data["metadata"]["artist"]
    mapper = data["metadata"]["mapper"]
    density = data["metadata"]["density"]
    notes_data = data["notes"]
    sleep(10)
    pygame.mixer.init()  # Initialize the mixer module
    pygame.mixer.music.load("songs/song_2013.wav")  # Load the music file
    pygame.mixer.music.play()  # Start playing the music

    # Step 4: Game loop
    running = True
    all_notes = []
    id_to_note = {}
    for note_data in notes_data:
        note = Note(note_data)
        all_notes.append(note)
        id_to_note[note.note_id] = note

    prev_ids_pairs = []
    for note in all_notes:
        for prev_id in note.prev_ids:
            if prev_id != 0:
                prev_ids_pairs.append((id_to_note[prev_id], note))
                id_to_note[prev_id].next_ids.append(note)

    pairs = []
    left = 0
    right = 1
    while right < len(all_notes):
        if all_notes[left].time == all_notes[right].time:
            pairs.append((all_notes[left], all_notes[right]))
            right += 1
        else:
            left += 1

    judgement_circles = []  # Store the judgement circles based on the number of lanes
    for i in range(num_lanes):
        position = (
            i * game.lane_width + game.lane_width // 2
        )  # Adjust the position based on the lane
        judgement_circle = JudgementCircle(position)
        judgement_circles.append(judgement_circle)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        music_position = pygame.mixer.music.get_pos() / 1000.0
        # Compare the music position with the game time to ensure synchronization
        # if abs(music_position - time) > 0.01:  # Adjust the threshold as needed
        #     # Adjust the game time to match the music position
        time = music_position

        # Step 5: Rendering
        game.game_window.fill((0, 0, 0))  # Clear the screen

        # Draw the lane lines
        lane_width = game.window_width // num_lanes
        for i in range(num_lanes):
            pygame.draw.line(
                game.game_window,
                (255, 255, 255),
                (i * lane_width, 0),
                (i * lane_width, game.window_height),
            )
        # draw connection lines
        for prev_ids_pair in prev_ids_pairs:
            prev_note, note = prev_ids_pair
            if prev_note.is_visible(time):
                start_line_point = prev_note.get_pos_based_on_time(time, game)
                end_line_point = note.get_pos_based_on_time(time, game)
                pygame.draw.line(
                    game.game_window,
                    (255, 255, 255),
                    start_line_point,
                    end_line_point,
                )

        # draw simultaneous notes lines
        for pair in pairs:
            note1 = pair[0]
            note2 = pair[1]
            if note1.is_visible(time) and note2.is_visible(time):
                start_line_point = note1.get_pos_based_on_time(time, game)
                end_line_point = note2.get_pos_based_on_time(time, game)
                pygame.draw.line(
                    game.game_window,
                    (255, 255, 255),
                    start_line_point,
                    end_line_point,
                )

        # Update and draw the notes
        for live_note in all_notes:
            live_note.draw(game, time)

        # Update and draw the judgement circles
        for judgement_circle in judgement_circles:
            judgement_circle.draw(game)

        pygame.display.flip()  # Update the game window
        game.clock.tick(60)  # Limit the frame rate
        # time += 1 / 60  # Update the time


pygame.quit()

if __name__ == "__main__":
    main()
