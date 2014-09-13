from flask import Flask, redirect, session, request, render_template, url_for, flash, jsonify, send_file, make_response, g, abort
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
import os, json
