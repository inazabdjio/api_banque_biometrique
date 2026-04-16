import face_recognition
import json
import numpy as np

class FaceService:
    @staticmethod
    def encode_face(image_file):
        # On remet le curseur au début du fichier au cas où il aurait été lu avant
        image_file.seek(0)
        try:
            image = face_recognition.load_image_file(image_file)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                # On transforme le premier visage trouvé en liste puis en chaîne JSON
                return json.dumps(encodings[0].tolist())
            return None
        except Exception:
            return None

    @staticmethod
    def verify_face(stored_encoding_str, current_image_file):
        try:
            # Conversion de la String JSON en tableau NumPy
            stored_encoding = np.array(json.loads(stored_encoding_str))
            
            current_image_file.seek(0)
            current_image = face_recognition.load_image_file(current_image_file)
            current_encodings = face_recognition.face_encodings(current_image)
            
            if not current_encodings:
                return False
            
            # Comparaison des visages
            # La tolérance par défaut est 0.6. Plus c'est bas, plus c'est strict.
            results = face_recognition.compare_faces([stored_encoding], current_encodings[0], tolerance=0.6)
            return bool(results[0])
        except Exception:
            return False