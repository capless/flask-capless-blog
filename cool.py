import kev
import formy

from envs import env
from flask import Flask, render_template, request, redirect, url_for
from kev.loading import KevHandler
from formy.kev import KEVForm

app = Flask(__name__)

kev_handler = KevHandler({
    's3':{
        'backend':'kev.backends.s3.db.S3DB',
        'connection':{
            'bucket':env('DATA_BUCKET')
        }
    },
})

ADMIN_PREFIX = env('ADMIN_PREFIX','/admin')

class Post(kev.Document):
    title = kev.CharProperty(required=True)
    slug = kev.SlugProperty(required=True,unique=True)
    body = kev.CharProperty(required=True)

    class Meta:
        use_db = 's3'
        handler = kev_handler


class PostForm(KEVForm):
    _template = 'formy.templates.form.bootstrap_template'

    title = formy.CharField(required=True)
    slug = formy.SlugField(required=True)
    body = formy.CKEditor(required=True)

    class Meta:
        document_class = Post


@app.route('/')
def posts():
    p = Post.all()
    return render_template('home.html',posts=p)

@app.route('/post/<slug>')
def post(slug):
    p = Post.objects().get({'slug':slug})
    return render_template('post.html',post=p)

@app.route('{}/posts/create/'.format(ADMIN_PREFIX),methods=['GET','POST'])
def create_post():
    if request.method == 'POST':
        data = {k:v for k,v in request.form.items()}
        f = PostForm(**data)
        f.validate()
        if f._is_valid:
            p = f.save()
            return redirect(url_for('list_posts'))
    else:
        f = PostForm()
    return render_template('admin/create.html',form=f)

@app.route('{}/posts/'.format(ADMIN_PREFIX))
def list_posts():
    p = Post.all()
    return render_template('admin/list.html', posts=p)

@app.route('{}/update/<slug>'.format(ADMIN_PREFIX),methods=['GET','POST'])
def update_post(slug):
    p = Post.objects().get({'slug':slug})
    if request.method == 'POST':
        data = {k: v for k, v in request.form.items()}
        f = PostForm(_initial=p,**data)
        f.validate()
        if f._is_valid:
            p = f.save()
            return redirect(url_for('list_posts'))
    else:
        f = PostForm(_initial=p)
    return render_template('admin/update.html',form=f,post=p)

@app.route('{}/delete/<slug>'.format(ADMIN_PREFIX),methods=['GET','POST'])
def delete_post(slug):
    p = Post.objects().get({'slug': slug})
    if request.method == 'POST':
        p.delete()
        return redirect(url_for('list_posts'))
    return render_template('admin/delete.html',post=p)


if __name__ == '__main__':
    app.run()
