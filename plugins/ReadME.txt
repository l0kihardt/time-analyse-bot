��װ��ʽ��
1) cd����ǰĿ¼
2) python setup.py install

������ʱ������ת��Ϊ���ֱ�׼��ʱ���ʽ��ʱ���ַ�����
1) ʱ��㣨timestamp����ʾĳһ����ʱ��ʱ��������; 
2) ʱ������timedelta����ʾʱ���������ʱ��������; 
3) ʱ�����䣨timespan���о�����ʼ�ͽ���ʱ����ʱ�����䣩��
����ʾ����Test.py

�������ַ��������⣬���鵱ǰ���뻷���Ƿ�Ϊutf-8����ʹ�����´��룺
import sys
reload(sys)
sys.setdefaultencoding('utf8')

���ڽڼ��յ����ӷ�����
1) ��resourceĿ¼�µ�holi_lunar(����)��holi_solar(����)�ļ��ڰ��ո�ʽ���������Ľ������ƺ�����
2) ��resourceĿ¼�µ�regex.txt�ļ��ڼ�����Ӧ���յ�����ƥ�䣬��ɾ��regex.pkl�����ļ�
3) ��TimeUnit���е�norm_setHoliday����ͬ��������յ�����ƥ��