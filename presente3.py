import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))  # guarda o caminho na variável basedir

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')  # o caminho do db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # vê as modificações no db

db = SQLAlchemy(app)  # armazena o banco de dados --presente3

# -----------------------------------------------------------------------------

# criando tabela com as salas de aula
class Sala(db.Model):
    idSala = db.Column(db.Integer, primary_key=True)
    nomeSala = db.Column(db.String(100), nullable=False)
    estudantes = db.relationship('Estudante', backref='sala')

    def __repr__(self):
        return f'<Sala {self.nomeSala}>'

# criando tabela com os alunos
class Estudante(db.Model):
    idEstudante = db.Column(db.Integer, primary_key=True)
    nomeEstudante = db.Column(db.String(100), nullable=False)
    salaEstudante = db.Column(db.Integer, db.ForeignKey('sala.idSala'))
    telefonePais = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Estudante {self.nomeEstudante}>'

# criando tabela de frequência
class Frequencia(db.Model):
    idFrequencia = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(15), nullable=False)
    nome = db.Column(db.String(100))
    presente = db.Column(db.Integer, default=False)

    def __repr__(self):
        return f'<Frequencia {self.data}>'

# ------------------------------------------------------------------------------------

# página inicial
@app.route('/')
def index():
    db.create_all()
    return render_template('index.html')

# página com a lista de todas as salas
@app.route('/salas/')
def salas():
    salas = Sala.query.all()
    return render_template('salas.html', salas=salas)


# página para criar sala
@app.route('/criar_sala/', methods=('GET', 'POST'))
def criar_sala():
    if request.method == 'POST':
        nomeSala = request.form['nomeSala']
        sala = Sala(nomeSala=nomeSala)
        db.session.add(sala)
        db.session.commit()

        return redirect(url_for('salas'))

    return render_template('criar_sala.html')

# página específica de cada sala
@app.route('/salas/<int:sala_id>/')
def sala(sala_id):
    sala = Sala.query.get_or_404(sala_id)
    estudantes = Estudante.query.filter(Estudante.salaEstudante == sala_id).order_by(func.lower(Estudante.nomeEstudante)).all()
    return render_template('sala.html', sala=sala, estudantes=estudantes)

# botão para deletar sala
@app.post('/salas/<int:sala_id>/delete_sala')
def delete_sala(sala_id):
    sala = Sala.query.get_or_404(sala_id)
    db.session.delete(sala)
    db.session.commit()
    return redirect(url_for('salas'))

# página para criar aluno
@app.route('/criar_aluno/', methods=('GET', 'POST'))
def criar_aluno():
    if request.method == 'POST':
        nomeEstudante = request.form['nomeEstudante']
        salaEstudante = request.form['salaEstudante']
        telefonePais = int(request.form['telefonePais'])

        estudante=Estudante(nomeEstudante=nomeEstudante,
                            salaEstudante=salaEstudante,
                            telefonePais=telefonePais)

        db.session.add(estudante)
        db.session.commit()

        return render_template('index.html')

    else:
        salas = Sala.query.all()
        return render_template('criar_aluno.html',salas=salas)

# botão para deletar aluno
@app.post('/delete_aluno/<int:estudante_id>/')
def delete_aluno(estudante_id):
    estudante = Estudante.query.get_or_404(estudante_id)
    db.session.delete(estudante)
    db.session.commit()
    return redirect(url_for('salas'))

# página para chamada
@app.route('/salas/<int:sala_id>/chamada/', methods=('GET', 'POST'))
def chamada(sala_id):
    if request.method == 'POST':
        sala = Sala.query.get_or_404(sala_id)

        data = str(request.form['data'])
        nomes = request.form.getlist('nome')
        presentes = request.form.getlist('presente')

        i = 0
        while i < len(nomes):

            if int(presentes[i]) == 1:
                frequencia = Frequencia(data=data,
                                        nome=nomes[i],
                                        presente=presentes[i])
                db.session.add(frequencia)
                db.session.commit()

            else:
                frequencia = Frequencia(data=data,
                                        nome=nomes[i],
                                        presente=presentes[i])
                db.session.add(frequencia)
                db.session.commit()

            i += 1

        return render_template('index.html', sala=sala)

    else:
        sala = Sala.query.get_or_404(sala_id)
        estudantes = Estudante.query.filter(Estudante.salaEstudante == sala_id).order_by(func.lower(Estudante.nomeEstudante)).all()
        return render_template('chamada.html', sala=sala, estudantes=estudantes)

# página para consulta de frequência
@app.route('/consulta/')
def consulta():
    salas = Sala.query.all()
    estudantes = Estudante.query.order_by(func.lower(Estudante.nomeEstudante)).all()
    return render_template('consulta.html', salas=salas, estudantes=estudantes)

# página específica do aluno para consulta de frequência
@app.route('/consulta/<int:estudante_id>/')
def consulta_aluno(estudante_id):
    estudante = Estudante.query.get_or_404(estudante_id)
    frequencias = Frequencia.query.filter(Frequencia.nome == estudante.nomeEstudante).all()
    return render_template('consulta_aluno.html', estudante=estudante, frequencias=frequencias)


# error.html (quando dá erro)
@app.route('/<string:nome>') #trás mais segurança e impede que o usuário insira nomes para links que não existem
def error(nome):
    variavel = f'Página ({nome}) não existe' #f é para as chaves funcionarem
    return render_template("error.html", variavel=variavel) #variavel1 é do html = variavel2 que é do python

# sobre
@app.route('/sobre')
def sobre():
    return render_template("sobre.html")

if __name__ == '__main__':
    app.run (debug=True)
