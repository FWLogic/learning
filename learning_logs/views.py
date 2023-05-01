from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')


def check_web_owner(request, web):
    """确认请求的网页属于当前用户"""
    if web.owner != request.user:
        raise Http404


@ login_required
def topics(request):
    """显示所有主题"""
    _topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': _topics}
    return render(request, 'learning_logs/topics.html', context)


@ login_required
def topic(request, topic_id):
    """显示单个主题及其所有条目"""
    _topic = Topic.objects.get(id=topic_id)
    check_web_owner(request, _topic)
    entries = _topic.entry_set.order_by('-date_added')
    context = {'topic': _topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@ login_required
def new_topic(request):
    """添加新的主题"""
    if request.method != 'POST':
        # 未提交数据：创建一个新表单
        form = TopicForm()
    else:
        # POST提交的数据,对数据进行处理
        form = TopicForm(request.POST)
        if form.is_valid():
            topic_new = form.save(commit=False)
            topic_new.owner = request.user
            topic_new.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@ login_required
def new_entry(request, topic_id):
    """添加新条目"""
    _topic = Topic.objects.get(id=topic_id)
    check_web_owner(request, _topic)
    if request.method != 'POST':
        # 未提交数据：创建一个新表单
        form = EntryForm()
    else:
        # POST提交的数据,对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            _new_entry = form.save(commit=False)
            _new_entry.topic = _topic
            _new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))
    context = {'topic': _topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@ login_required
def edit_entry(request, entry_id):
    """编辑条目"""
    entry = Entry.objects.get(id=entry_id)
    _topic = entry.topic
    check_web_owner(request, _topic)
    if request.method != 'POST':
        # 初次请求，使用当前条目填充表单
        form = EntryForm(instance=entry)
    else:
        # POST提交的数据，对数据进行处理
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[_topic.id]))
    context = {'entry': entry, 'topic': _topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
