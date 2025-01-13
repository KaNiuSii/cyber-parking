import cv2
import numpy as np
from models.server_response import ServerResponse


class ServerResponseFrame:
    @staticmethod
    def write_server_response(resp: ServerResponse) -> np.ndarray:
        frame_width, frame_height = 400, 300
        response_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

        text_data = resp.model_dump()

        y_offset = 20
        line_height = 20
        margin = 10

        for key, value in text_data.items():
            if isinstance(value, list):
                value_str = " | ".join(map(str, value))
            else:
                value_str = str(value)

            text = f"{key.capitalize()}: {value_str}"

            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            max_text_width = frame_width - 2 * margin
            while text_size[0] > max_text_width:
                split_idx = text[:max_text_width // 7].rfind(' ')
                wrapped_line = text[:split_idx]
                remaining_line = text[split_idx + 1:]

                cv2.putText(
                    response_frame,
                    wrapped_line,
                    (margin, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )
                y_offset += line_height

                text = remaining_line
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]

            cv2.putText(
                response_frame,
                text,
                (margin, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
            y_offset += line_height

            if y_offset > frame_height - line_height:
                break

        return response_frame
    