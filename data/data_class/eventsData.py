class EventsData:
    def __init__(self, titlu, categorie, data_start, estimare_participanti, nivel_importanta, locatie_nume, tip_detaliat):
        self.titlu = titlu
        self.categorie = categorie
        self.data_start = data_start
        self.estimare_participanti = estimare_participanti
        self.nivel_importanta = nivel_importanta
        self.locatie_nume = locatie_nume
        self.tip_detaliat = tip_detaliat

    def __str__(self):
        return f"Event: {self.titlu}, Date: {self.data_start}, Location: {self.locatie_nume}, Category: {self.categorie} , Estimated Attendance: {self.estimare_participanti}, Importance Level: {self.nivel_importanta}, Detailed Type: {', '.join(self.tip_detaliat)}"